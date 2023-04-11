from Data import Timestamp, Run, Vent
from DataCollection import initDataCollection

# Function for curve analysis
def function():
    two = 2
    return two

# Main driver code
def main():
    from time import time
    from threading import Thread
    from Communication import send_louver_position,subscribe_to_multicast

    testing = True
    testingTime = 600 # seconds

    # Init vent(s)
    vents = [Vent(33), Vent(1), Vent(2)]
    targetTemps = [70, 74, 75]
    for vent, target in zip(vents, targetTemps):
        vent.setTarget(target)

    initDataCollection(vents)

    startTime = time()
    def updateVent(ventUUID: int, temperature: float, motion: bool):
        print(f"Message received: {ventUUID = }, {temperature = }, {motion = }")
        for vent in vents:
            if testing and time() - startTime > testingTime:
                quit()
            if vent.id == ventUUID:
                newLouverPosition = vent.update(temperature, motion)
                print("New louver position: ", newLouverPosition*120)
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
  
