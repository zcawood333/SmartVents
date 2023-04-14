from Data import Timestamp, Run, Vent
from DataCollection import initDataCollection, writeVentParams

# Function for curve analysis
def localCurveCheck():

    # get an aggregated curve that we can compare against

    # what we are intrested in checking is the strady state behavior of the curves
    #how do we figure out if a curve has reached steady state?
    two = 2
    return two

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
    targetTemps = [59, 80, 75]
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
    # userAlertsThread = Thread(target=, args=())

    controlThread.start()
    # userAlertsThread.start()


if __name__ == "__main__":
    main()
  
