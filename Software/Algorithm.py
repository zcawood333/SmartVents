from Data import Timestamp, Run, Vent

# Function for autocorrel.
def function1():
    one = 1
    return one

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
    testingTime = 30 # seconds

    # Init vent(s)
    vents = [Vent(0), Vent(1), Vent(2)]
    targetTemps = [73, 74, 75]
    for vent, target in zip(vents, targetTemps):
        vent.setTarget(target)

    startTime = time()
    def updateVent(ventUUID: int, temperature: float, motion: bool):
        for vent in vents:
            if testing and time() - startTime > testingTime:
                quit()
            if vent.id == ventUUID:
                newLouverPosition = vent.update(temperature, motion)
                send_louver_position(ventUUID, newLouverPosition)
                break
        else:
            print("Error. Message could not be paired with a vent.")

    controlThread = Thread(target=subscribe_to_multicast, args=(updateVent,))
    # userAlertsThread = Thread(target=, args=())

    controlThread.start()
    # userAlertsThread.start()

if __name__ == "__main__":
    main()
