from Data import Timestamp
from Data import Run
from Data import Vent
#does this work?
# also import ccmmunciation stuff

# Function for autocorrel.
def funcion1():
    one = 1
    return one

# Function for curve analysis
def function():
    two = 2
    return two


# Main driver code
testing = True

# Init vent(s)
vents = [Vent(0), Vent(1), Vent(2)]
for vent in vents:
    vent.setTarget(75.2)

# Control loop
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
    if(testing):
        break


