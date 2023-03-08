#include <vector>
#include <cstdint>
#include "Data.h"

class Vent {
private:
	uint64_t id; // Vent uuid
	uint64_t zone; // Specifies the zone of the vent
	float louver; // Current louver position [0-1]
	Run currentRun; // Stores the current run information
	std::vector<Run> pastRuns; // Stores past run information

public:
	Vent(uint64_t id, uint64_t zone);
	Vent(uint64_t id);
	uint64_t getId();
	void setZone(uint64_t zone);
	uint64_t getZone();
	void setLouverPos(float newPos);
	float getLouverPos();
	Run getCurrentRun();
	std::vector<Run> getPastRuns();
	void updateCurrentRun(RunTimestamp data); // Adds a new timestamp to the current run
	void saveCurrentRun(); // Adds the current run to the pastRuns
};
