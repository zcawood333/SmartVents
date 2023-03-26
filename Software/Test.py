from typing import List

# Defines data structures used for the temperature algorithm ~ currently subject to change

TIMESTAMP_DELAY = 600  # The delay between timestamps measured in seconds (was 300)

class RunTimestamp:
    def __init__(self, louver: float, measured: float, estimated: float):
        self.louver = louver  # Louver position [0-1]
        self.measured = measured  # Measured temperature in C
        self.estimated = estimated  # Estimated temperature in C


class Run:
    def __init__(self, run_id: int, target_temp: float, start_temp: float):
        self.run_id = run_id  # Identifies the run
        self.run_time = 0  # Total time the run took in seconds
        self.target_temp = target_temp  # The target temperature of the run
        self.start_temp = start_temp  # The temperature the run started at
        self.timestamps: List[RunTimestamp] = []  # All the timestamps collected over the run

    def add_timestamp(self, data: RunTimestamp):
        self.timestamps.insert(0, data)  # Add timestamp at the beginning of the list

    def save(self, past_runs: List['Run']):
        saved = Run(self.run_id, self.target_temp, self.start_temp)  # Create a copy of the run
        saved.run_time = self.run_time
        saved.timestamps = self.timestamps.copy()
        if len(past_runs) >= 1024:  # Maximum number of runs we will save
            past_runs.pop()  # Remove the oldest run from past_runs
        past_runs.insert(0, saved)  # Add the saved run at the beginning of the list


class Vent:
    def __init__(self, id: int, zone: int = 0):
        self.id = id  # Vent uuid
        self.zone = zone  # Specifies the zone of the vent
        self.louver = 1  # Current louver position [0-1]
        self.current_run: Run = None  # Stores the current run information
        self.past_runs: List[Run] = []  # Stores past run information

    def set_zone(self, zone: int):
        self.zone = zone

    def get_zone(self):
        return self.zone

    def set_louver_pos(self, new_pos: float):
        self.louver = new_pos

    def get_louver_pos(self):
        return self.louver

    def start_run(self, target: float, data: RunTimestamp):
        self.current_run = Run(len(self.past_runs) + 1, target, data.estimated)  # Create a new run
        self.current_run.add_timestamp(data)

    def update_current_run(self, data: RunTimestamp):
        self.current_run.run_time += TIMESTAMP_DELAY
        self.current_run.add_timestamp(data)

    def save_current_run(self):
        if self.current_run is None:
            return
        self.current_run.save(self.past_runs)
        self.current_run = None

    def get_current_run(self):
        return self.current_run

    def get_past_runs(self):
        return self.past_runs.copy()

    def get_id(self):
        return self.id
    
import math

class RunTimestamp:
    def __init__(self, louver, measured, estimated):
        self.louver = louver
        self.measured = measured
        self.estimated = estimated

class Run:
    def __init__(self, runId, runTime, targetTemp, startTemp, timestamps):
        self.runId = runId
        self.runTime = runTime
        self.targetTemp = targetTemp
        self.startTemp = startTemp
        self.timestamps = timestamps

class Vent:
    def __init__(self, ventId):
        self.ventId = ventId
        self.currentRun = None

    def startRun(self, targetTemp, baseline):
        run = Run(1, 0, targetTemp, baseline.measured, [baseline])
        self.currentRun = run

    def getCurrentRun(self):
        return self.currentRun

    def updateCurrentRun(self, timestamp):
        self.currentRun.timestamps.append(timestamp)

TIMESTAMP_DELAY = 600

def estimateTemp(vent):
    last = vent.getCurrentRun().timestamps[1]  # Assumed 1 (last timestamp) is when we started ~ probably need better specics later
    current = vent.getCurrentRun().timestamps[0]  # Current timestamp (must update this before calling this function!)
    delay = TIMESTAMP_DELAY  # again this may need to change depending on which timestamp was the lower ~ 

    # Temp euqation ~ will need testing ~ HEAVY approx.
    avgRoomMass = 30  # kg, rough estimate
    avgBubbleMass = 1.5  # kg, very rough esimtate
    M = avgBubbleMass / avgRoomMass
    # s = 1.005  # kJ/kg K specific heat of air
    adjust = (last.measured - current.measured) / 40

    # heatToRoom = avgBubbleMass * s * (last.measured - current.measured)  # calc heat transfered from the bubble to the room
    # roomDT = heatToRoom / (avgRoomMass * s)  # calculate the delta T of the room based on heat transfered to it
    roomDT = M * (last.measured - current.measured) - adjust
    print("Estimated dT: ", roomDT)
    return current.estimated + roomDT

if __name__ == "__main__":
    vent = Vent(0)
    baseline = RunTimestamp(0, 22.22, 22.22)
    vent.startRun(23.89, baseline)
    maxVentTemp = 31.3
    estimate = vent.getCurrentRun().timestamps[0].estimated
    time = 0

    while estimate < vent.getCurrentRun().targetTemp:
        # simulate reaching cutoff
        stopTimestamp = RunTimestamp(0, maxVentTemp, estimate)
        vent.updateCurrentRun(stopTimestamp)
        time += TIMESTAMP_DELAY

        # Simulate the cooling period (10min for now)
        startTimestamp = RunTimestamp(1, 26.5, estimate)
        vent.updateCurrentRun(startTimestamp)
        time += TIMESTAMP_DELAY

        # Estimate the new temp
        estimate = estimateTemp(vent)
        print("New Estimate: ", estimate, "\n")
    
    print("Total Time: ", time)

