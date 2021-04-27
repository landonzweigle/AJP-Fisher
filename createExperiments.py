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

    def addExperiment(self, framesPerTrial, nTrials, n_epochs, learningRate, gamma):
        newExperiment = {("expr%d"%self.experimentCount):{
            "framesPerTrial":framesPerTrial,
            "nTrials":nTrials,
            "n_epochs":n_epochs,
            "learningRate":learningRate,
            "gamma":gamma
        }}
        self.internalDict.update(newExperiment)
        self.experimentCount += 1

    def toDict(self,):
        return pds.DataFrame(self.internalDict).T


def main():
    # experiments = {"exp1": {"some key": "some value", "some col": "some value 2"}}
    experiments = ExperimentsList()

    experiments.addExperiment(1,2,3,4,5)
    experiments.addExperiment(6,7,8,9,10)



    csvPath.mkdir(parents=True, exist_ok=True) #make the dir if it doesnt exist.
    df = experiments.toDict()
    print(df)
    df.to_csv(csvFullPath)

if __name__ == "__main__":
    main()