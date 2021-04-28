import sys
import createExperiments

def main(runnerName):
    if not runnerName == "keegan" and not runnerName == "landon":
        print("Please pass landon or keegan as the runner")

    print("Running experiments for", runnerName)

    # Create the csv files
    createExperiments.main(runnerName)

    # For each line in the csv file:


if __name__ == "__main__":
    runnerName = sys.argv[1]
    main(runnerName)