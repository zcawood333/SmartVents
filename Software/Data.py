# Defines data structs/classes needed for hub

class Timestamp:
    louverPos = 0.0 # Louver position measured as a float from 0 - 1. Defines position from the start of this timestanp to end (creation of next timestamp)
    temperature = 0.0 # Measured temperature when timestamp was created (F)
    motion = False # Motion at the moment of timestamp creation
    
    def __init__(self, louverPos, temperature, motion):
        self.louverPos = louverPos
        self.temperature = temperature
        self.motion = motion
    
class Run:
    target = 0 # Target temperature for the run in F
    timestamps = None # List of timestamps for the run

    def __init__(self, target):
        self.target = target
    
    def createTimestamp(self, timestamp): # Inserts a timestamp into the beginning of timestamps list [newer -> older]
        self.timestamps.insert(0, timestamp)
            
    def removeTimestamp(self, ind): # Removes the timestamp at index ind, does nothing if the index is out of bounds
        if ind < len(self.timestamps):
            del self.timestamps[ind]
        
    def getTimestamp(self, ind): # Returns the timestamp from the given position, None of the index is out of bounds
        if ind < len(self.timestamps):
            return self.timestamps[ind]
        else:
            return None
        
class Vent:
    id = 0
    runs = None
    heatCoeff = None

    def __init__(self, id):
        self.id = id

    def setTarget(self, target): # Sets the target temperature of the vent. Also starts a new run (make sure to handle closing the old run...)
        newRun = Run(target)
        self.runs.insert(0, newRun)

    def update(): # see ventupt function from meeting notes
        stuff = None
        #get new lovver pos
        #record as new timestamp 
        #send the data to the vent
        #profit???