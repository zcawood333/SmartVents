# Defines data structs/classes needed for hub
import numpy as np
from datetime import datetime

from DataCollection import writeData

class Timestamp:
    def __init__(self, louverPos: float, temperature: float, motion: bool):
        self.louverPos = louverPos # Louver position measured as a float from 0 - 1. Defines position from the start of this timestanp to end (creation of next timestamp)
        self.temperature = temperature # Measured temperature when timestamp was created (F)
        self.motion = motion # Motion at the moment of timestamp creation
        current_time = datetime.now()
        self.unix_time = current_time.timestamp()
       
       

class Run:
    def __init__(self, target: float):
        self.target = target # Target temperature for the run in F
        self.timestamps = list() # List of timestamps for the run
    
    def createTimestamp(self, timestamp: Timestamp): # Inserts a timestamp into the beginning of timestamps list [newer -> older]
        self.timestamps.insert(0, timestamp)
            
    def removeTimestamp(self, ind: int): # Removes the timestamp at index ind, does nothing if the index is out of bounds
        if ind < len(self.timestamps):
            del self.timestamps[ind]
        
    def getTimestamp(self, ind: int): # Returns the timestamp from the given position, None of the index is out of bounds
        if ind < len(self.timestamps):
            return self.timestamps[ind]
        else:
            return None
        
class Vent:
    instances = []

    def __init__(self, id: int, master: bool = False):
        Vent.instances.append(self)
        self.id = id
        self.master = master
        self.runs = list()
        self.userTarget = 72 # Target temperature (F) when the vent is "enabled" due to motion
        self.__heatingCoeffs = np.empty((1,0)) # Represents sigma in tp'=sigma*p*c
        self.heatConstant = 1 # Represents c in tp'=sigma*p*c
        self.bucket = 0
        self.bucketMax = 4
        self.enabled = True

    @property
    def heatingCoeffs(self):
        if self.__heatingCoeffs.size != len(Vent.instances):
            self.__heatingCoeffs = np.matrix([0]*len(Vent.instances)).T
            self.__heatingCoeffs[Vent.instances.index(self), 0] = 1
        return self.__heatingCoeffs

    @heatingCoeffs.setter
    def heatingCoeffs(self, newCoeffs: np.matrix):
        self.__heatingCoeffs = newCoeffs

    @property
    def idleTarget(self):
        return self.userTarget - 4

    @property
    def target(self):
        return self.userTarget if self.enabled else self.idleTarget

    @property
    def currLouverPosition(self):
        if len(self.runs) > 0 and len(self.runs[0].timestamps) > 0:
            return self.runs[0].timestamps[0].louverPos
        else:
            return 0

    # Vent 
    def setTarget(self, target): # Sets the target temperature of the vent. Also starts a new run (make sure to handle closing the old run...)
        self.userTarget = target
        newRun = Run(target)
        self.runs.insert(0, newRun)

    def update(self, measured: float, motion: bool): # Runs an update upon being woken up by the vent ~ Do we do this is driver code or in class functions?
        # Check if the vent should become idle
        previouslyEnabled = self.enabled
        self.__updateIdleTimer(motion)
        if previouslyEnabled and not self.enabled:
            self.__setIdle()
        elif not previouslyEnabled and self.enabled:
            self.__resume()

        # Get the new louver postion based on the measured temperature
        newPos = self.__getNewPos(measured)

        # Record a new timestamp
        if len(self.runs) > 0:
            newTimestamp = Timestamp(newPos, measured, motion)
            self.runs[0].createTimestamp(newTimestamp)
        else:
            print("Error, vent %d has not had it's target temperature set yet.\n", self.id)

        if len(self.runs[0].timestamps) >= 10 and self.runs[0].timestamps[-1].temperature < self.runs[0].timestamps[0].temperature:
            self.__recalibrate()

        # Write the new timestamp info to the data file
        writeData(self.id, self.target, measured, newPos, motion)

        # Return the new louver position after creating the new timestamp
        return newPos

    # Internal vent behavior functions
    def __getNewPos(self, measured: float): # Calculates a new louver position and returns it
        target = self.userTarget if self.enabled else self.idleTarget
        deltaT = target - measured
        if self.master:
            deltaT /= 2
        otherLouverPos = np.matrix([vent.currLouverPosition for vent in Vent.instances if vent != self]).T
        otherHeatingCoeffs = np.matrix([self.heatingCoeffs[Vent.instances.index(vent), 0] for vent in Vent.instances if vent != self]).T
        pos =  (deltaT / self.heatConstant - otherLouverPos.T * otherHeatingCoeffs) / self.heatingCoeffs[Vent.instances.index(self), 0]
        pos = pos[0,0]
        pos = max(0, min(1, pos))
        return pos

    def __updateIdleTimer(self, motion: bool):
        if motion:
            self.bucket = min(self.bucketMax, self.bucket + 1)
        else:
            self.bucket = max(0, self.bucket - 2)
        if self.bucket == 0:
            self.enabled = False
        else:
            self.enabled = True

    def __setIdle(self):
        newRun = Run(self.idleTarget)
        self.runs.insert(0, newRun)

    def __resume(self):
        newRun = Run(self.userTarget)
        self.runs.insert(0, newRun)

    def __recalibrate(self):
        oldHeatConstant = self.heatConstant
        self.__setHeatConstant()
        if not self.__setHeatCoeff(): # if setting the heat coefficient vector fails
            self.heatConstant = oldHeatConstant
            print(f'Error recalibrating vent {self.id}')
        else:
            print(f'Vent {self.id} recalibrated successfully')


    def __setHeatConstant(self):
        for run in self.runs:
            for timestamp0, timestamp1 in zip(run.timestamps,run.timestamps[1:]):
                deltaT = timestamp1.temperature - timestamp0.temperature
                if deltaT > 0 and timestamp0.louverPos > 0:
                    self.heatConstant = deltaT / timestamp0.louverPos
                    return

    def __retimedLouverPosCurve(self, timestamps: list[Timestamp]):
        if timestamps == self.runs[0].timestamps[:-1]:
            return np.matrix([timestamp.louverPos for timestamp in timestamps]).T
        retimedLouverPosCurve = list()
        for timestamp in timestamps:
            time = timestamp.unix_time
            if len(self.runs) == 0 or (len(self.runs) == 1 and len(self.runs[0].timestamps) == 0): # if no timestamps have been recorded yet there will only be 1 empty run
                retimedLouverPosCurve.append(0)
                continue
            if len(self.runs[-1].timestamps) > 0 and time < self.runs[-1].timestamps[-1].unix_time: # timestamp older than oldest timestamp for this vent
                retimedLouverPosCurve.append(0)
                continue
            elif time < self.runs[-2].timestamps[-1].unix_time: # timestamp older than oldest timestamp for this vent and first run is empty
                retimedLouverPosCurve.append(0)
                continue
            if time > self.runs[0].timestamps[0].unix_time: # timestamp more recent than most recent timestamp for this vent
                retimedLouverPosCurve.append(self.runs[0].timestamps[0].louverPos)
                continue
            previousTimestampTime = self.runs[0].timestamps[0].unix_time
            foundTimestamp = False
            for idx, run in enumerate(self.runs): # runs from most recent run to oldest
                for timestamp in run.timestamps: # runs from most recent timestamps to oldest
                    if time < previousTimestampTime and time > timestamp.unix_time:
                        retimedLouverPosCurve.append(timestamp.louverPos)
                        foundTimestamp = True
                        break
                    else:
                        previousTimestampTime = timestamp.unix_time
                if foundTimestamp:
                    break
                # if time < run.timestamps[-1].unix_time and self.runs.index(run) != 0:
                #     retimedLouverPosCurve.append(self.runs[self.runs.index(run)-1].timestamps[-1].louverPos)
                #     break
                # foundInCurrentRun = False
                # for timestamp0, timestamp1 in zip(run.timestamps, run.timestamps[1:]):
                #     if timestamp0.unix_time < time and timestamp1.unix_time >= time:
                #         retimedLouverPosCurve.append(timestamp0.louverPos)
                #         foundInCurrentRun = True
                #         break
                # if foundInCurrentRun:
                #     break
                # elif self.runs.index(run) == len(self.runs)-1:
                #     retimedLouverPosCurve.append(run.timestamps[-1].louverPos)
                #     break
        retimedLouverPosCurve = np.matrix(retimedLouverPosCurve).T
        return retimedLouverPosCurve

    def __setHeatCoeff(self) -> bool:
        deltaTCurve = list()
        louverPosCurves = np.empty((len(self.runs[0].timestamps)-1, 0))
        for vent in Vent.instances:
            louverPosCurves = np.concatenate((louverPosCurves, vent.__retimedLouverPosCurve(self.runs[0].timestamps[:-1])), axis=1)
        for timestamp0, timestamp1 in zip(self.runs[0].timestamps, self.runs[0].timestamps[1:]):
            deltaT = timestamp1.temperature - timestamp0.temperature
            deltaTCurve.append(deltaT)
        deltaTCurve = np.matrix(deltaTCurve).T
        try:
            self.heatingCoeffs = np.linalg.inv(louverPosCurves.T * louverPosCurves) * louverPosCurves.T * (deltaTCurve/self.heatConstant)
            return True
        except np.linalg.LinAlgError:
            return False
