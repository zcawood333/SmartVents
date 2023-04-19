# Defines data structs/classes needed for hub
import numpy as np
from datetime import datetime

from DataCollection import writeData, writeVentParams

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
    BASIC_SYSTEM = False # Forces louvers to be always open
    DUMB_SMART_SYSTEM = True
    instances = []
    minTemperature = 60 # Minimum temperature we will allow

    def __init__(self, id: int, master: bool = False, localControl: bool = False):
        Vent.instances.append(self)
        self.id = id
        self.master = master
        self.localControl = localControl
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
        return max(self.userTarget - 8, self.minTemperature)

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
        if(target >= self.minTemperature):
            self.userTarget = target
        else:
            print("Error vent minimum temperature is", self.minTemperature, "F. Setting target to minimum...")
            self.userTarget = self.minTemperature
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
            print("Error, vent", self.id, "has not had it's target temperature set yet.")

        if len(self.runs[0].timestamps) >= 3 and self.runs[0].timestamps[-1].temperature < self.runs[0].timestamps[0].temperature:
            self.__recalibrate()

        # Write the new timestamp info to the data file
        writeData(self.id, self.target, measured, newPos, motion)

        # Return the new louver position after creating the new timestamp
        return newPos

    # Internal vent behavior functions
    def __getNewPos(self, measured: float): # Calculates a new louver position and returns it
        if self.BASIC_SYSTEM: # System with no louver control, only thermostat
            return 1
        if self.DUMB_SMART_SYSTEM:
            if measured > self.target:
                return 0
            else:
                return 1
        if measured > self.target:
            return 0
        target = self.userTarget if self.enabled else self.idleTarget
        deltaT = target - measured
        if self.master and not all([vent.currLouverPosition <= 0.1 for vent in Vent.instances if not vent.master]):
            deltaT /= 2
        otherLouverPos = np.matrix([vent.currLouverPosition for vent in Vent.instances if vent != self]).T
        otherHeatingCoeffs = np.matrix([self.heatingCoeffs[Vent.instances.index(vent), 0] for vent in Vent.instances if vent != self]).T
        if self.localControl:
            otherLouverPos = np.matrix([0]).T
            otherHeatingCoeffs = np.matrix([0]).T
        pos =  (deltaT / self.heatConstant - otherLouverPos.T * otherHeatingCoeffs) / self.heatingCoeffs[Vent.instances.index(self), 0]
        pos = pos[0,0]
        pos = max(0, min(1, pos))
        return pos

    def __updateIdleTimer(self, motion: bool):
        if motion:
            self.bucket = min(self.bucketMax, self.bucket + 2)
        else:
            self.bucket = max(0, self.bucket - 1)
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
        oldHeatCoeffs = self.heatingCoeffs
        self.__setHeatConstant()
        if self.heatConstant < 0 or not self.__setHeatCoeff(): # if setting the heat coefficient vector fails
            self.heatConstant = oldHeatConstant
            self.heatingCoeffs = oldHeatCoeffs
            # print(f'Error recalibrating vent {self.id}')
        else:
            # print(f'Vent {self.id} recalibrated successfully')
            writeVentParams(self.id, self.master, self.localControl, self.heatConstant, self.heatingCoeffs, Vent.instances.index(self))

    def __setHeatConstant(self):
        previousHeatConstant = self.heatConstant
        for run in self.runs:
            for timestamp0, timestamp1 in zip(run.timestamps,run.timestamps[1:]):
                deltaT = timestamp0.temperature - timestamp1.temperature
                if deltaT > 0 and timestamp0.louverPos > 0.5:
                    self.heatConstant = deltaT / timestamp0.louverPos
                    self.heatConstant = 0.75*previousHeatConstant + 0.25*self.heatConstant
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
            if len(self.runs[-1].timestamps) > 0 and time <= self.runs[-1].timestamps[-1].unix_time: # timestamp older than oldest timestamp for this vent
                retimedLouverPosCurve.append(0)
                continue
            elif len(self.runs) >= 2 and time <= self.runs[-2].timestamps[-1].unix_time: # timestamp older than oldest timestamp for this vent and first run is empty
                retimedLouverPosCurve.append(0)
                continue
            if time >= self.runs[0].timestamps[0].unix_time: # timestamp more recent than most recent timestamp for this vent
                retimedLouverPosCurve.append(self.runs[0].timestamps[0].louverPos)
                continue
            previousTimestampTime = self.runs[0].timestamps[0].unix_time
            foundTimestamp = False
            for idx, run in enumerate(self.runs): # runs from most recent run to oldest
                for timestamp in run.timestamps: # runs from most recent timestamps to oldest
                    if time <= previousTimestampTime and time > timestamp.unix_time:
                        retimedLouverPosCurve.append(timestamp.louverPos)
                        foundTimestamp = True
                        break
                    else:
                        previousTimestampTime = timestamp.unix_time
                if foundTimestamp:
                    break
        retimedLouverPosCurve = np.matrix(retimedLouverPosCurve).T
        return retimedLouverPosCurve

    def __setHeatCoeff(self) -> bool:
        previousHeatCoeffs = self.heatingCoeffs
        deltaTCurve = list()
        louverPosCurves = np.empty((len(self.runs[0].timestamps)-1, 0))
        for vent in Vent.instances:
            if not self.localControl or vent == self:
                louverPosCurves = np.concatenate((louverPosCurves, vent.__retimedLouverPosCurve(self.runs[0].timestamps[:-1])), axis=1)
        for timestamp0, timestamp1 in zip(self.runs[0].timestamps, self.runs[0].timestamps[1:]):
            deltaT = timestamp0.temperature - timestamp1.temperature
            deltaTCurve.append(deltaT)
        deltaTCurve = np.matrix(deltaTCurve).T
        if all([louverPos == 0 for louverPos in self.__retimedLouverPosCurve(self.runs[0].timestamps[:-1])]):
            return False
        if not all([deltaT > 0 for deltaT in deltaTCurve]):
            return False
        try:
            self.heatingCoeffs = np.linalg.inv(louverPosCurves.T * louverPosCurves) * louverPosCurves.T * (deltaTCurve/self.heatConstant)
            self.heatingCoeffs = 0.75*previousHeatCoeffs + 0.25*self.heatingCoeffs
            if self.heatingCoeffs[Vent.instances.index(self), 0] <= 0:
                raise Exception('bad recalibration')
            # for idx, heatCoeff in enumerate(self.heatingCoeffs):
            #     if idx == Vent.instances.index(self):
            #         self.heatingCoeffs[idx] = max(0, heatCoeff)
            # if not all([heatCoeff > 0 for heatCoeff in self.heatingCoeffs]):
            #     raise Exception('bad recalibration')
            return True
        except Exception:
            return False
