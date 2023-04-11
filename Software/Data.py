# Defines data structs/classes needed for hub
import numpy as np
from DataCollection import writeData

class Timestamp:
    def __init__(self, louverPos: float, temperature: float, motion: bool):
        self.louverPos = louverPos # Louver position measured as a float from 0 - 1. Defines position from the start of this timestanp to end (creation of next timestamp)
        self.temperature = temperature # Measured temperature when timestamp was created (F)
        self.motion = motion # Motion at the moment of timestamp creation

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
        self.heatingCoeff = [1] # Represents sigma in tp'=sigma*p*c
        self.heatConstant = 1 # Represents c in tp'=sigma*p*c
        self.bucket = 0
        self.bucketMax = 4
        self.enabled = True

    @property
    def idleTarget(self):
        return self.userTarget - 4

    @property
    def target(self):
        return self.userTarget if self.enabled else self.idleTarget

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

        if len(self.runs[0].timestamps) >= 10 and self.runs[0].timestamps[-1].temperature > self.runs[0].timestamps[0].temperature:
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
        pos = deltaT / (self.heatConstant * self.heatingCoeff[0])
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
        self.__setHeatConstant()
        self.__setHeatCoeff()

    def __setHeatConstant(self):
        for run in self.runs:
            for timestamp0, timestamp1 in zip(run.timestamps,run.timestamps[1:]):
                deltaT = timestamp1.temperature - timestamp0.temperature
                if deltaT > 0 and timestamp0.louverPos > 0:
                    self.heatConstant = deltaT / timestamp0.louverPos
                    return

    def __setHeatCoeff(self):
        deltaTCurve = list()
        louverPosCurve = list()
        for timestamp0, timestamp1 in zip(self.runs[0].timestamps, self.runs[0].timestamps[1:]):
            deltaT = timestamp1.temperature - timestamp0.temperature
            deltaTCurve.append(deltaT)
            louverPosCurve.append(timestamp0.louverPos)
        deltaTCurve = np.matrix(deltaTCurve).T
        louverPosCurve = np.matrix(louverPosCurve).T
        self.heatingCoeff = np.linalg.inv(louverPosCurve.T * louverPosCurve) * louverPosCurve.T * (deltaTCurve/self.heatConstant)
