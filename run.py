#!/usr/bin/python3

import sys
import createExperiments
sys.path.insert(1, 'AutoFisher-Python/')
import AutoFisher
import subprocess
import time
import os


FNULL = open(os.devnull, 'w')
experimentDir = "./Experiments/"

def main(runnerName):
    if not runnerName == "keegan" and not runnerName == "landon":
        print("Please pass landon or keegan as the runner")

    print(os.getcwd())

    print("Running experiments for", runnerName)

    print("Writing the experiments to", createExperiments.csvFullPath)
    createExperiments.main(runnerName)

    print("Reading experiments from", createExperiments.csvFullPath)
    csvFile = open(createExperiments.csvFullPath)
    for i,line in enumerate(csvFile):
        if i != 0:
            realIdx = i-1
            expDir = ""
            expNtmp = "EXP_%d/" % (realIdx)

            expRunDir = os.path.join(experimentDir, expNtmp)
            if(os.path.exists(expRunDir)):
                print("skipping experiment %d" % realIdx)
                continue

            subprocess.Popen(["./gradlew", "run"],stdout=FNULL, stderr=subprocess.STDOUT)
            time.sleep(5)
            print("Running experiment:", line)

            try:
                AutoFisher.main(realIdx, experimentDir)
            except Exception as err:
                print(err)
                print("Experiment %d failed (unexpected error)." % realIdx)

if __name__ == "__main__":
    runnerName = sys.argv[1]
    main(runnerName)