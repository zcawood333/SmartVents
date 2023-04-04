from Data import Timestamp
from Data import Run
from Data import Vent
#does this work?
# also import ccmmunciation stuff

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

    testing = True
    testingTime = 30 # seconds

    # Init vent(s)
    vents = [Vent(0), Vent(1), Vent(2)]
    targetTemps = [73, 74, 75]
    for vent, target in zip(vents, targetTemps):
        vent.setTarget(target)

    # Control loop
    startTime = time()
    while(True):
        # Wait for messages
        #while(nomessage):

        # Read the message
        measured = 000
        motion = False
        vid = 0

        # Select the proper vent and update
        if vid <= len(vents) - 1:
            newPos = vents[vid].update(measured)
        else:
            print("Error. Message could not be paired with a vent.")

        # Send a message back to the vent with the new louver postion
        #send(newPos)

        # so we don't loop forever...
        if(testing and time() - startTime > testingTime):
            break

if __name__ == "__main__":
    main()
