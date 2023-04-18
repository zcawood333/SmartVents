import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from DataCollection import dataFileName, parameterFileName

def plotVentData(ventDataDirPath: os.PathLike, ventUUIDs: list[int] = None,):
    dataFiles = [file for file in os.listdir(ventDataDirPath) if file.endswith("data.csv")]
    filePaths = [os.path.join(ventDataDirPath, dataFile) for dataFile in dataFiles]
    if ventUUIDs is not None:
        filePaths = [os.path.join(ventDataDirPath, dataFileName(ventUUID)) for ventUUID in ventUUIDs]
    for filePath in filePaths:
        df = pd.read_csv(filePath, sep="|", parse_dates=["Timestamp "], )
        if len(df.index) == 0:
            continue
        df.columns = df.columns.str.strip()
        df["Timestamp"] = df["Timestamp"].apply(lambda time: time - df["Timestamp"][0])
        df.set_index("Timestamp", inplace=True)
        df["Motion"] = df["Motion"].str.strip().apply(lambda motion: motion == "True")
        df.plot(title=os.path.basename(filePath).split(".")[0], include_bool=True, subplots=[["Measured Temperature", "Target Temperature"],["Motion", "LouverPosition"]], layout=(2,1), sharex=True, legend=True)
        plt.savefig(os.path.join(ventDataDirPath, os.path.basename(filePath).split(".")[0] + ".png"))
        # plt.show()
        plt.close()

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
        df.set_index("Timestamp", inplace=True)
        df["Heat Coefficients"] = df["Heat Coefficients"].str.replace("[", "").str.replace("]", "").str.replace('"', "").str.strip()
        newHeatCoeffCols = [f'Heat Coefficient {i}' for i in range(df["Heat Coefficients"][0].count(",") + 1)]
        df[newHeatCoeffCols] = df["Heat Coefficients"].str.split(", ", expand=True)
        for col in newHeatCoeffCols:
            df[col] = df[col].astype(float)
        selfHeatCoeffIndex = df["Self Heat Coefficient Index"][0]
        df = df.drop(columns=["Self Heat Coefficient Index"])
        plt.figure(idx)
        plt.title(os.path.basename(filePath).split(".")[0])
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


if __name__ == "__main__":
    dirPath = os.path.join(os.path.dirname(__file__), "../Data")
    dirPath = os.path.join(dirPath, os.listdir(dirPath)[-1])
    dirPath = os.path.join(dirPath, os.listdir(dirPath)[-1])
    plotVentData(dirPath)
    plotVentParams(dirPath)
