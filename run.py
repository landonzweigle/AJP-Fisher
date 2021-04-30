import sys
import createExperiments
sys.path.insert(1, 'AutoFisher-Python/')
import AutoFisher
import subprocess


def main(runnerName):
    if not runnerName == "keegan" and not runnerName == "landon":
        print("Please pass landon or keegan as the runner")

    print("Running experiments for", runnerName)

    print("Writing the experiments to", createExperiments.csvFullPath)
    createExperiments.main(runnerName)

    print("Reading experiments from", createExperiments.csvFullPath)
    csvFile = open(createExperiments.csvFullPath)
    for i,line in enumerate(csvFile):
        if i != 0:
            print("Running experiment:", line)
            subprocess.Popen(["./gradlew" "run"])
            AutoFisher.main(i-1)

if __name__ == "__main__":
    runnerName = sys.argv[1]
    main(runnerName)