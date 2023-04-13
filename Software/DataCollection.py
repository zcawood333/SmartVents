import os
import datetime as dt
import numpy as np

DATA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "../Data")
DATE_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, dt.datetime.now().date().isoformat())
TIME_FOLDER_PATH = os.path.join(DATE_FOLDER_PATH, dt.datetime.now().strftime("%H-%M-%S"))

def ventDataPath(ventUUID: int):
    return os.path.join(TIME_FOLDER_PATH, f"{ventUUID}_data.csv")

def ventParameterPath(ventUUID: int):
    return os.path.join(TIME_FOLDER_PATH, f"{ventUUID}_params.csv")

def initDataCollection(vents: list):
    if not os.path.isdir(DATA_FOLDER_PATH):
        os.mkdir(DATA_FOLDER_PATH)
    if not os.path.isdir(DATE_FOLDER_PATH):
        os.mkdir(DATE_FOLDER_PATH)
    if not os.path.isdir(TIME_FOLDER_PATH):
        os.mkdir(TIME_FOLDER_PATH)
    for vent in vents:
        ventDataFilePath = ventDataPath(vent.id)
        ventParameterFilePath = ventParameterPath(vent.id)
        if not os.path.isfile(os.path.join(TIME_FOLDER_PATH, ventDataFilePath)):
            with open(ventDataFilePath, "w") as file:
                file.write("Timestamp, Target Temperature, Measured Temperature, LouverPosition, Motion\n")
        if not os.path.isfile(os.path.join(TIME_FOLDER_PATH, ventParameterFilePath)):
            with open(ventParameterFilePath, "w") as file:
                file.write("Timestamp, Master Vent, Heat Constant, Heat Coefficients, Self Heat Coefficient Index\n")

def writeData(ventUUID: int, targetTemp: float, measuredTemp: float, louverPosition: float, motion: bool):
    with open(ventDataPath(ventUUID), "a") as file:
        file.write(f"{dt.datetime.now().isoformat()}, {targetTemp}, {measuredTemp}, {louverPosition}, {motion}\n")

def writeVentParams(ventUUID: int, master: bool, heatConstant: float, heatCoeffs: np.matrix, selfHeatCoeffIndex: int):
    with open(ventParameterPath(ventUUID), "a") as file:
        file.write(f"{dt.datetime.now().isoformat()}, {master}, {heatConstant}, {heatCoeffs.tolist()}, {selfHeatCoeffIndex}\n")
