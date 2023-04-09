import os
import datetime as dt

DATA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "../Data")
DATE_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, dt.datetime.now().date().isoformat())
TIME_FOLDER_PATH = os.path.join(DATE_FOLDER_PATH, dt.datetime.now().strftime("%H-%M-%S"))

def ventPath(ventUUID: int):
    return os.path.join(TIME_FOLDER_PATH, f"{ventUUID}.csv")

def initDataCollection(vents: list["Vent"]):
    if not os.path.isdir(DATA_FOLDER_PATH):
        os.mkdir(DATA_FOLDER_PATH)
    if not os.path.isdir(DATE_FOLDER_PATH):
        os.mkdir(DATE_FOLDER_PATH)
    if not os.path.isdir(TIME_FOLDER_PATH):
        os.mkdir(TIME_FOLDER_PATH)
    data_file_paths = []
    for vent in vents:
        vent_file_path = ventPath(vent.id)
        data_file_paths.append(vent_file_path)
        if not os.path.isfile(os.path.join(TIME_FOLDER_PATH, vent_file_path)):
            with open(vent_file_path, "w") as file:
                file.write("Timestamp, Target Temperature, Measured Temperature, LouverPosition, Motion\n")

def writeData(ventUUID: int, targetTemp: float, measuredTemp: float, louverPosition: float, motion: bool):
    with open(ventPath(ventUUID), "a") as file:
        file.write(f"{dt.datetime.now().isoformat()}, {targetTemp}, {measuredTemp}, {louverPosition}, {motion}\n")
