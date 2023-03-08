#include <iostream>
#include <cmath>
#include "Vent.h"

#define TIMESTAMP_DELAY 300 // The delay between timestamps measured in seconds

float estimateTemp(Vent &vent) {
    RunTimestamp last = vent.getCurrentRun().timestamps[1]; // Assumed 1 (last timestamp) is when we started ~ probably need better specics later
    RunTimestamp current = vent.getCurrentRun().timestamps[0]; // Current timestamp (must update this before calling this function!)
    uint64_t delay = TIMESTAMP_DELAY; //again this may need to change depending on which timestamp was the lower ~ 

    // Temp euqation ~ will need testing ~ HEAVY approx.
    float avgRoomMass = 30; //kg, rough estimate
    float avgBubbleMass = 1; //kg, very rough esimtate
    float s = 1.005; //kJ/kg K specific heat of air

    float heatToRoom = avgBubbleMass * s * (last.measured - current.measured); //calc heat transfered from the bubble to the room
    float roomDT = heatToRoom / (avgRoomMass * s); //calculate the delta T of the room based on heat transfered to it
    return current.estimated + roomDT;
}

int main(int argc, char* argv[]) {
    // in order to estiamte a temp, 1st update the current time stamp,
    //float newEstimate = estimateTemp(vent.getCurrentRun, vent);
    

    // do some calcs with the estiamted temp & get a new pos

    //set the new position of the lovuer
    //vent.setLouverPos(newpos);

    //send the louver pos

    return 0;
}
