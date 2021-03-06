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
	
	# total frame counts = [50000 , 100000 , 200000]
	# fpt vals = [25,50,100]
	# hidden layer archs = [ [20], [50], [100], [50,50], [30,80], [80,30], [40,40,40], [20,80,20], [80,20,80] ]
	
    if runnerName == "landon":
	    experiments.addExperiment(25, 2000, [20], 100, 0.01, 0.8)
	    experiments.addExperiment(25, 4000, [100], 100, 0.01, 0.8)
	    experiments.addExperiment(25, 8000, [40,40,40], 100, 0.01, 0.8)
	    experiments.addExperiment(25, 2000, [30,80], 100, 0.01, 0.8)
	    experiments.addExperiment(25, 4000, [50,50], 200, 0.01, 0.8)
	    
	    experiments.addExperiment(50, 1000, [30,80], 200, 0.01, 0.8)
	    experiments.addExperiment(50, 2000, [100], 200, 0.01, 0.8)
	    experiments.addExperiment(50, 4000, [50], 200, 0.01, 0.8)
	    experiments.addExperiment(50, 1000, [80,20,80], 300, 0.01, 0.8)
	    
	    experiments.addExperiment(100, 500, [40,40,40], 300, 0.01, 0.8)
	    experiments.addExperiment(100, 1000, [80,20,80], 300, 0.01, 0.8)
	    experiments.addExperiment(100, 2000, [50,50], 300, 0.01, 0.8)
	    experiments.addExperiment(100, 500, [50], 100, 0.01, 0.8)
	    experiments.addExperiment(100, 1000, [20], 100, 0.01, 0.8)
    elif runnerName == "keegan":
	    experiments.addExperiment(25, 8000, [50], 100, 0.01, 0.8)
	    experiments.addExperiment(25, 2000, [80,20,80], 100, 0.01, 0.8)
	    experiments.addExperiment(25, 4000, [20,80,20], 200, 0.01, 0.8)
	    experiments.addExperiment(25, 8000, [80,30], 200, 0.01, 0.8)
	    
	    experiments.addExperiment(50, 2000, [50,50], 200, 0.01, 0.8)
	    experiments.addExperiment(50, 4000, [80,30], 200, 0.01, 0.8)
	    experiments.addExperiment(50, 1000, [20], 300, 0.01, 0.8)
	    experiments.addExperiment(50, 2000, [20,80,20], 300, 0.01, 0.8)
	    experiments.addExperiment(50, 4000, [40,40,40], 300, 0.01, 0.8)
	    
	    experiments.addExperiment(100, 2000, [20,80,20], 300, 0.01, 0.8)
	    experiments.addExperiment(100, 500, [80,30], 100, 0.01, 0.8)
	    experiments.addExperiment(100, 1000, [30,80], 200, 0.01, 0.8)
	    experiments.addExperiment(100, 2000, [100], 300, 0.01, 0.8)
		
    csvPath.mkdir(parents=True, exist_ok=True) #make the dir if it doesnt exist.
    df = experiments.toDict()
    print(df)
    df.to_csv(csvFullPath)

if __name__ == "__main__":
    runnerName = sys.argv[1]
    main(runnerName)
