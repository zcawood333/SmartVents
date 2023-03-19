#include <iostream>
#include <cmath>
#include "Vent.h"

float estimateTemp(Vent &vent) {
    RunTimestamp last = vent.getCurrentRun().timestamps[1]; // Assumed 1 (last timestamp) is when we started ~ probably need better specics later
    RunTimestamp current = vent.getCurrentRun().timestamps[0]; // Current timestamp (must update this before calling this function!)
    uint64_t delay = TIMESTAMP_DELAY; //again this may need to change depending on which timestamp was the lower ~ 

    // Temp euqation ~ will need testing ~ HEAVY approx.
    float avgRoomMass = 30; //kg, rough estimate
    float avgBubbleMass = 1.5; //kg, very rough esimtate
    float M = avgBubbleMass / avgRoomMass;
    //float s = 1.005; //kJ/kg K specific heat of air

    //float heatToRoom = avgBubbleMass * s * (last.measured - current.measured); //calc heat transfered from the bubble to the room
    //float roomDT = heatToRoom / (avgRoomMass * s); //calculate the delta T of the room based on heat transfered to it
    float roomDT = M * (last.measured - current.measured);
    std::cout << "Estimated dT: " << roomDT << "\n";
    return current.estimated + roomDT;
}

int main(int argc, char* argv[]) {

    Vent vent(0);
    RunTimestamp baseline = {1, 22.3, 22.3};
    vent.startRun(23.89, baseline);
    float maxVentTemp = 33.3;
    float estimate = vent.getCurrentRun().timestamps[0].estimated;
    uint32_t time = 0;

    while(estimate < vent.getCurrentRun().targetTemp) {
        //simulate reaching cutoff
        RunTimestamp stopTimestamp = {0, maxVentTemp, estimate};
        vent.updateCurrentRun(stopTimestamp);
        time += TIMESTAMP_DELAY;

        //Simulate the cooling period (10min for now)
        RunTimestamp startTimestamp = {1, 26.7, estimate};
        vent.updateCurrentRun(startTimestamp);
        time += TIMESTAMP_DELAY;

        // Estimate the new temp
        estimate = estimateTemp(vent);
        std::cout << "New Estimate: " << estimate << "\n\n";
    }
    std::cout << "Total Time: " << time << "\n";

    // in order to estiamte a temp, 1st update the current time stamp,
    //float newEstimate = estimateTemp(vent.getCurrentRun, vent);
    

    // do some calcs with the estiamted temp & get a new pos

    //set the new position of the lovuer
    //vent.setLouverPos(newpos);

    //send the louver pos

    return 0;
}
