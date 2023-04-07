#include <string>
#include "Vent.h"
//#include "Data.h"

Vent::Vent(uint64_t id, uint64_t zone) {
	this->id = id;
	this->zone = zone;
	this->louver = 1;
}

Vent::Vent(uint64_t id) {
	this->id = id;
	this->zone = 0;
	this->louver = 1;
}

Vent::~Vent() {
    // free all the runs and run timestamps
}

uint64_t Vent::getId() {
	return id;
}

void Vent::setZone(uint64_t zone) {
	this->zone = zone;
}

uint64_t Vent::getZone() {
	return zone;
}

void Vent::setLouverPos(float newPos) {
	this->louver = newPos;
}

float Vent::getLouverPos() {
	return louver;
}

Run Vent::getCurrentRun() {
	return currentRun;
}

std::vector<Run> Vent::getPastRuns() {
	return pastRuns;
}

void Vent::startRun(float target, RunTimestamp data) {
	currentRun.runId = 0;
	currentRun.runTime = 0;
	currentRun.targetTemp = target;
	currentRun.startTemp = data.estimated;
	currentRun.timestamps.clear();
	currentRun.timestamps.insert(currentRun.timestamps.begin(), data);
}

void Vent::updateCurrentRun(RunTimestamp data) { // Smaller index = Newer data
	currentRun.runTime += TIMESTAMP_DELAY;
	currentRun.timestamps.insert(currentRun.timestamps.begin(), data);
}

void Vent::saveCurrentRun() { // Smaller index = Newer runs
	Run saved = currentRun; //probably needs a copy constructor
	uint32_t windowSize = 1024; // Maximum number of runs we will save
	if(pastRuns.size() > windowSize) {
		pastRuns.pop_back();
	}
	pastRuns.insert(pastRuns.begin(), saved);
}