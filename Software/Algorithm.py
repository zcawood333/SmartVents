from Data import Timestamp, Run, Vent
from DataCollection import initDataCollection, writeVentParams
from UserFeedback import MyClass

# Functions for curve analysis
def getStableTimestamp(run : Run, target): # Returns the index of the first stable timestamp, None if the run isn't stable

    stableRange = 3 # +- range from target to be considered stable
    minDuration = 3 # Minimum number of timestamps that need to be in the stable range to be considered stable
    stability = 0 # Counts number of stable timestamps

    for timestamp in run.timestamps:
        if target + stableRange >= timestamp.temperature and target - stableRange <= timestamp.temperature:
            stability += 1

            if stability >= minDuration:
                return run.timestamps.index(run) - minDuration + 1
        else:
            if stability > 0:
                stability -= 1
        
    return None

def localCurveCheck(vent : Vent):
    # For now we will a assume a curve is in steady state when it first reaches within +-3F of its target & maintains it for at least 3 timestamps
    # This means that it may be possible to get runs that never reach steady state (if that happens what do we do?)

    minPastRuns = 3 # Minimum number of past runs with the same target temperature needed to run the analysis

    # Get the current target temperature
    if(len(vent.runs) > 0):
        currentTarget = vent.runs[0].target
    else:
        print("Error. No runs found for the current vent.")
        return

    # Find all the stable past runs that have the same target temperature as the current run
    pastRuns = list()
    for run in vent.runs[1:]:
        if(run.target == currentTarget and getStableTimestamp(run) != None):
            pastRuns.append(run)

    #
    if(len(pastRuns) >= minPastRuns):
        # now that we potentially have the steady states of the past curves, what do we do?
        two = 0
    else:
        print("Error. Number of matching past runs is insufficient.")
        return

# Main driver code
def main():
    from time import time
    from threading import Thread
    from Communication import send_louver_position,subscribe_to_multicast

    testing = True
    testingTime = 6000 # seconds

    LOCAL_CONTROL = False

    # Init vent(s)
    vents = []
    UUIDs = [100, 200, 300]
    masterVent = [False, False, False]
    targetTemps = [70, 80, 75]
    for id, master, target in zip(UUIDs, masterVent, targetTemps):
        vent = Vent(id, master, LOCAL_CONTROL)
        vent.setTarget(target)
        vents.append(vent)

    initDataCollection(vents)
    for vent in vents:
        writeVentParams(vent.id, vent.master, vent.localControl, vent.heatConstant, vent.heatingCoeffs, Vent.instances.index(vent))

    startTime = time()
    def updateVent(ventUUID: int, temperature: float, motion: bool):
        print(f"Message received: {ventUUID = }, {temperature = :.2f}, {motion = }")
        for vent in vents:
            if testing and time() - startTime > testingTime:
                quit()
            if vent.id == ventUUID:
                newLouverPosition = vent.update(temperature, motion)
                print(f'New louver position: {newLouverPosition*120:.2f}')
                send_louver_position(ventUUID, newLouverPosition*120)
                break
        else:
            print("Error. Message could not be paired with a vent.")

    controlThread = Thread(target=subscribe_to_multicast, args=(updateVent,))
    my_class = MyClass()
    userAlertsThread = Thread(target= my_class.User_Alerts, args=())

    controlThread.start()
    userAlertsThread.start()


if __name__ == "__main__":
    main()
  
