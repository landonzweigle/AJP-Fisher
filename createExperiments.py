#!/usr/bin/python3

import sys
import pandas as pds, os
from pathlib import Path

csvName = "experiments.csv"
csvDir = "./Experiments/"
csvFullPath = os.path.join(csvDir, csvName)
csvPath = Path(csvDir)



# framesPerTrial = 200 #amount in frames
# nTrials = 100

# n_epochs = 50
# learningRate = 0.01

# finalEpsilon = 0.0001
# gamma = 0.8


class ExperimentsList():
    internalDict = None

    experimentCount = 0
    def __init__(self):
        self.internalDict = {}

    def addExperiment(self, framesPerTrial, nTrials, nHiddens, n_epochs, learningRate, gamma):
        newExperiment = {("expr%d"%self.experimentCount):{
            "framesPerTrial":framesPerTrial,
            "nTrials":nTrials,
            "nHiddens": nHiddens,
            "n_epochs":n_epochs,
            "learningRate":learningRate,
            "gamma":gamma
        }}
        self.internalDict.update(newExperiment)
        self.experimentCount += 1

    def toDict(self,):
        return pds.DataFrame(self.internalDict).T


def main(runnerName):
    if not runnerName == "keegan" and not runnerName == "landon":
        print("Please pass landon or keegan as the runner")
        
    experiments = ExperimentsList()

    # framesPerTrial, nTrials, nHiddens, n_epochs, learningRate, gamma
    # 5 35 100 250 500
    # 200 400
    if runnerName == "keegan":
        experiments.addExperiment(150, 2500, [35], 100, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [100, 100], 200, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [500, 250], 200, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [100, 35, 100], 300, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [500, 250, 500], 300, 0.01, 0.8)
        experiments.addExperiment(1000, 2500, [500], 100, 0.01, 0.8)
        experiments.addExperiment(1000, 2500, [35, 100, 35], 300, 0.01, 0.8)
    elif runnerName == "landon":
        experiments.addExperiment(150, 2500, [5], 100, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [500], 100, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [250, 500], 200, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [35, 100, 35], 300, 0.01, 0.8)
        experiments.addExperiment(150, 2500, [100, 250, 100], 300, 0.01, 0.8)
        experiments.addExperiment(1000, 2500, [5], 100, 0.01, 0.8)
        experiments.addExperiment(1000, 2500, [100, 100], 200, 0.01, 0.8)

    csvPath.mkdir(parents=True, exist_ok=True) #make the dir if it doesnt exist.
    df = experiments.toDict()
    print(df)
    df.to_csv(csvFullPath)

if __name__ == "__main__":
    runnerName = sys.argv[1]
    main(runnerName)
