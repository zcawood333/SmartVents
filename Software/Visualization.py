import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from DataCollection import dataFileName, parameterFileName

combinedFigure = plt.figure(0)

def plotVentData(ventDataDirPath: os.PathLike, ventUUIDs: list[int] = None,):
    dataFiles = [file for file in os.listdir(ventDataDirPath) if file.endswith("data.csv")]
    filePaths = [os.path.join(ventDataDirPath, dataFile) for dataFile in dataFiles]
    if ventUUIDs is not None:
        filePaths = [os.path.join(ventDataDirPath, dataFileName(ventUUID)) for ventUUID in ventUUIDs]
    frames = list()
    for filePath in filePaths:
        df = pd.read_csv(filePath, sep="|", parse_dates=["Timestamp "], )
        if len(df.index) == 0:
            continue
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time - df["Timestamp"][0])
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time.total_seconds())
        ventIdx = os.path.basename(filePath).split('_')[0]
        df.set_index("Timestamp", inplace=True)
        df["Motion"] = df["Motion"].str.strip().apply(lambda motion: motion == "True")
        df.rename(columns={"Measured Temperature": f'Vent {ventIdx} Measured Temperature', "Target Temperature": f'Vent {ventIdx} Target Temperature', "Motion": f'Vent {ventIdx} Motion', "LouverPosition": f'Vent {ventIdx} LouverPosition'}, inplace=True, errors="raise")
        ventIdx = os.path.basename(filePath).split('_')[0]
        frames.append((ventIdx, df))
        #plt.savefig(os.path.join(ventDataDirPath, os.path.basename(filePath).split(".")[0] + ".png"))
    fig, ax = plt.subplots(2, 1, sharex=True)

    for ventIdx, frame in frames:
        frame.plot(title="Vent Data", xlabel="Time (s)", ax=ax, subplots=[[f"Vent {ventIdx} Measured Temperature", f"Vent {ventIdx} Target Temperature"],[f"Vent {ventIdx} Motion", f"Vent {ventIdx} LouverPosition"]])
    for idx, subplot in enumerate(ax):
        ylabels = ["Temperature (F)", "Louver Position %"]
        subplot.ylabel = ylabels[idx]
        subplot.legend(loc = 'best', fontsize = 'xx-small')
    # plt.show()
    plt.close()
    # dataFiles = [file for file in os.listdir(ventDataDirPath) if file.endswith("data.csv")]
    # filePaths = [os.path.join(ventDataDirPath, dataFile) for dataFile in dataFiles]
    # if ventUUIDs is not None:
    #     filePaths = [os.path.join(ventDataDirPath, dataFileName(ventUUID)) for ventUUID in ventUUIDs]
    # for filePath in filePaths:
    #     df = pd.read_csv(filePath, sep="|", parse_dates=["Timestamp "], )
    #     if len(df.index) == 0:
    #         continue
    #     df.columns = df.columns.str.strip()
    #     df["Timestamp"] = df["Timestamp"].apply(lambda time: time - df["Timestamp"][0])
    #     df["Timestamp"] = df["Timestamp"].apply(lambda time: time.total_seconds())
    #     df.set_index("Timestamp", inplace=True)
    #     df["Motion"] = df["Motion"].str.strip().apply(lambda motion: motion == "True")
    #     ventIdx = os.path.basename(filePath).split('_')[0]
    #     df.rename(columns={"Measured Temperature": f'Vent {ventIdx} Measured Temperature', "Target Temperature": f'Vent {ventIdx} Target Temperature', "Motion": f'Vent {ventIdx} Motion', "LouverPosition": f'Vent {ventIdx} LouverPosition'}, inplace=True, errors="raise")
    #     df.plot(ax=combinedFigure, title=f'Vent {ventIdx} Data', include_bool=True, subplots=[[f"Vent {ventIdx} Measured Temperature", f'Vent {ventIdx} Target Temperature'],[f'Vent {ventIdx} Motion', f'Vent {ventIdx} LouverPosition']], layout=(2,1), sharex=True, legend=True, xlabel='Time (s)')
        # plt.savefig(os.path.join(ventDataDirPath, os.path.basename(filePath).split(".")[0] + ".png"))
        # plt.show()
        # plt.close()

def plotVentParams(ventParamDirPath: os.PathLike, ventUUIDs: list[int] = None,):
    parameterFiles = [file for file in os.listdir(ventParamDirPath) if file.endswith("params.csv")]
    filePaths = [os.path.join(ventParamDirPath, parameterFile) for parameterFile in parameterFiles]
    if ventUUIDs is not None:
        filePaths = [os.path.join(ventParamDirPath, parameterFileName(ventUUID)) for ventUUID in ventUUIDs]
    for idx, filePath in enumerate(filePaths):
        df = pd.read_csv(filePath, sep="|", parse_dates=["Timestamp "], )
        if len(df.index) == 0:
            continue
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time - df["Timestamp"][0])
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time.total_seconds())
        df.set_index("Timestamp", inplace=True)
        df["Heat Coefficients"] = df["Heat Coefficients"].str.replace("[", "").str.replace("]", "").str.replace('"', "").str.strip()
        newHeatCoeffCols = [f'Heat Coefficient {i}' for i in range(df["Heat Coefficients"][0].count(",") + 1)]
        df[newHeatCoeffCols] = df["Heat Coefficients"].str.split(", ", expand=True)
        for col in newHeatCoeffCols:
            df[col] = df[col].astype(float)
        selfHeatCoeffIndex = df["Self Heat Coefficient Index"][0]
        df = df.drop(columns=["Self Heat Coefficient Index"])
        ventIdx = os.path.basename(filePath).split('_')[0]
        plt.figure(idx)
        plt.title(f'Vent {ventIdx} Parameters')
        plt.plot(df.index, df["Heat Constant"], label="Heat Constant")
        for idx, col in enumerate(newHeatCoeffCols):
            if idx == selfHeatCoeffIndex:
                plt.plot(df.index, df[col], label="Self Heat Coefficient")
            else:
                plt.plot(df.index, df[col], label=col)
        plt.legend(loc="upper left", bbox_to_anchor=(0,1), fontsize="xx-small")
        plt.xlabel("Time (s)")
        plt.savefig(os.path.join(ventParamDirPath, os.path.basename(filePath).split(".")[0] + ".png"))
        # plt.show()
        plt.close()


def plotMainHeat(dirPath: os.PathLike):
    parameterFiles = [os.path.join(dirPath, file) for file in os.listdir(dirPath) if file.endswith("params.csv")]
    for filePath in parameterFiles:
        ventId = None
        df = pd.read_csv(filePath, sep="|", parse_dates=["Timestamp "], )
        df.columns = df.columns.str.strip()
        if df["Master Vent"][0].strip() != "True":
            continue
        ventId = os.path.basename(filePath).split("_")[0]
        filePath = os.path.join(dirPath, dataFileName(int(ventId)))
        df = pd.read_csv(filePath, sep="|", parse_dates=["Timestamp "], )
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time - df["Timestamp"][0])
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time.total_seconds())
        df.set_index("Timestamp", inplace=True)
        df["Main Heat On"] = df["Measured Temperature"] < df["Target Temperature"]
        newMainHeat = df.loc[:, "Main Heat On"].values
        lastTurnOff = None
        stillLockedOut = False
        for idx, val in enumerate(newMainHeat):
            if not val and newMainHeat[idx - 1]:
                lastTurnOff = df.index[idx]
                stillLockedOut = True
            if stillLockedOut:
                if df.index[idx] - lastTurnOff <= 180:
                    newMainHeat[idx] = False
                else:
                    stillLockedOut = False
        df.loc[:, "Main Heat On"] = newMainHeat
        firstTargetTime = None
        lastTargetTime = None
        for time, row in df.iterrows():
            if firstTargetTime is None and row["Measured Temperature"] > row["Target Temperature"]:
                firstTargetTime = time
            if row["Measured Temperature"] > row["Target Temperature"]:
                lastTargetTime = time
        totalEnergyCountMask = (df.index >= firstTargetTime) & (df.index < lastTargetTime) & (df["Main Heat On"] == True)
        totalEnergyCount = totalEnergyCountMask.sum()
        averageEnergyUsage = totalEnergyCount / (lastTargetTime - firstTargetTime)
        with open(os.path.join(dirPath, "energyCalculations.txt"), "w") as f:
            f.write(f'Energy Calculations\n')
            f.write(f'Total Energy Count: {totalEnergyCount}\n')
            f.write(f'Starting Time: {firstTargetTime}\n')
            f.write(f'Ending Time: {lastTargetTime}\n')
            f.write(f'Total Energy Time: {lastTargetTime - firstTargetTime}\n')
            f.write(f'Average Energy Usage: {averageEnergyUsage}\n')
        df.plot(title="Main Heat On/Off", include_bool=True, y=["Main Heat On"], legend=False, ylim=(0,1.1), xlabel='Time (s)')
        plt.savefig(os.path.join(dirPath, "mainHeatOn.png"))
        # plt.show()
        plt.close()
        break



if __name__ == "__main__":
    # dirPath = os.path.join(os.path.dirname(__file__), "../Data")
    # dirPath = os.path.join(dirPath, os.listdir(dirPath)[-1])
    # dirPath = os.path.join(dirPath, os.listdir(dirPath)[-1])
    dirPath = r'C:\Users\zcawo\Documents\School\Grad\firstYearGrad\secondSemester\ECE695I2I-II\SmartVents\Gold Masters\Dumb'
    plotVentData(dirPath)
    plt.savefig(os.path.join(dirPath, "combinedPlot.png"))
    plotVentParams(dirPath)
    plotMainHeat(dirPath)
