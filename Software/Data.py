# Defines data structs/classes needed for hub

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
    def __init__(self, id: int):
        self.id = id
        self.runs = list()
        self.heatCoeff = list()

    def setTarget(self, target): # Sets the target temperature of the vent. Also starts a new run (make sure to handle closing the old run...)
        newRun = Run(target)
        self.runs.insert(0, newRun)

    def update(self, measured: float): # Runs an update upon being woken up by the vent ~ Do we do this is driver code or in class functions?
        # Run some function to get a new louver position
        newPos = 1

        # Record a new timestamp
        if(len(self.runs) > 0):
            #newTimestamp = Timestamp(newPos, measured, motion~where do do we get this from)
            #self.runs[0].createTimestamp(newTimestamp)
            print("Create new ts\n")
        else:
            print("Error, vent %d has not had it's target temperature set yet.\n", self.id)

        # Send the data to the vent
        #send(newPos)???