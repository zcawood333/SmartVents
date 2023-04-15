import sys
import os
import random as r
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "../../Software"))

from Data import Timestamp, Run, Vent
from DataCollection import initDataCollection, writeData, writeVentParams


def enableDisableVent():
    return r.random() < 1/10


def motionDetected(roomActive: bool):
    motionDetectionChanceWhileActive = 0.9
    motionDetectionChanceWhileInactive = 0.05
    if roomActive:
        return r.random() < motionDetectionChanceWhileActive
    else:
        return r.random() < motionDetectionChanceWhileInactive


def temperatureNoise():
    return r.gauss(0, 1)/20


def changeRoomActivity(roomActive: bool):
    chanceRoomBecomesInactive = 1/20
    chanceRoomBecomesActive = 1/30
    if roomActive:
        return r.random() < chanceRoomBecomesInactive
    else:
        return r.random() < chanceRoomBecomesActive


class Room():
    def __init__(self, trueVent: Vent, simVent: Vent, startTemperature: float, active: bool):
        self.trueVent = trueVent
        self.simVent = simVent
        self.currTemperature = startTemperature
        self.active = active
        self.localControl = trueVent.localControl
    def update(self):
        self.currTemperature += self.trueVent.heatConstant * self.trueVent.heatingCoeffs.T * np.matrix([vent.currLouverPosition for vent in Vent.instances]).T
        self.currTemperature = self.currTemperature[0,0]
        self.currTemperature -= self.currTemperature/100 + temperatureNoise()
        self.currTemperature += temperatureNoise()
        if changeRoomActivity(self.active):
            self.active = not self.active
        self.simVent.update(self.currTemperature, motionDetected(self.active))


# control flags
USE_SEED = True
RAND_SEED = 0
LOCAL_CONTROL = True
NUM_VENTS = 10
NUM_CYCLES_TO_RUN = 1000
PERCENT_ROOMS_ACTIVE = 0.2

# random seed
if USE_SEED:
    r.seed(RAND_SEED)

# true vents/params
TARGET_TEMPS = [r.randint(70, 80) for i in range(NUM_VENTS)]
print(TARGET_TEMPS)
true_vents = [Vent(i, i==0, False) for i in range(NUM_VENTS)]
for vent in true_vents:
    vent.setTarget(TARGET_TEMPS[vent.id])
    vent.heatingCoeffs = np.matrix([r.random()/10 for i in range(NUM_VENTS)]).T
    vent.heatingCoeffs[vent.id,0] = r.random()/10 + 0.9
    vent.heatConstant = r.random()*2 + 1
Vent.instances.clear()

# simulation vents/params
simulation_vents = [Vent(i, i==0, LOCAL_CONTROL) for i in range(NUM_VENTS)]
for vent in simulation_vents:
    vent.setTarget(TARGET_TEMPS[vent.id])

# rooms
rooms = [Room(true_vents[i], simulation_vents[i], r.randint(60, 70), r.random() < PERCENT_ROOMS_ACTIVE) for i in range(NUM_VENTS)]

# data collection
initDataCollection(simulation_vents)

# simulation loop
for _ in range(NUM_CYCLES_TO_RUN):
    for room in rooms:
        room.update()
