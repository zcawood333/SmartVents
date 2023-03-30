// Defines data structes used for the temperature algorithm ~ currently subject to change
#include <cstdint>
#include <vector>

#define TIMESTAMP_DELAY 600 // The delay between timestamps measured in seconds (was 300)

typedef struct RunTimestamp {
	float louver; // Louver position [0-1]
	float measured; // Measured temperature in C
	float estimated; // Estimated temperature in C
} RunTimestamp;

typedef struct Run {
	uint64_t runId; // Indentifies the run
	uint64_t runTime; // Total time the run took in seconds
	float targetTemp; // The target temperature of the run
	float startTemp; // The temperature the run started at
	std::vector<RunTimestamp> timestamps; // All the timestamps collected over the run
} Run;