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

# Init vent(s)
vent1 = Vent(0)
vent1.setTarget(75.2)
testing = True

# Control loop
while(True):
    # wait for comm data?

    # read the message

    # do stuff

    # profit
    print(vent1.runs[0].target)

    # so we don't loop forever...
    if(testing):
        break


