#!/usr/bin/python3

import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


import RLNN, math, sys
import JavaPythonComms as JPComms
from numpy.core.defchararray import split
import numpy as np, pandas as pds


modesExcpected = {"TRAIN": ("FrameAtTime", "SafePractice"),"TEST": ("PersonPlay", "Practice"),"NORMAL": ("PersonPlay", "Normal")}
ExperimentsCSV = "experiments.csv"

expDir = "../Experiments"
expNtmp = "EXP_%d/"

RLNNDumpName = "RLNN.dump"

myDir = Path(os.path.join(expDir, "default/"))




################################################
# Set up standardization
################################################

def sampleSTD(values, avg):
    sqrSum = sum([(val - avg)**2 for val in values])
    div = sqrSum / (len(values) - 1)
    return math.sqrt(div)

deltaP = [-1, 0, 1]
nVel = [-1, 0, 1]

validActions = [0,1] #[reel out, reel in]
meanAct = 0.5
stdAct = 0.5

reinforcements = [0,1,2,3]
meanRein = np.mean(reinforcements)  #1.5
stdRein = np.std(reinforcements)    #1.118



Xmeans = [np.mean(x) for x in [deltaP, nVel, nVel, validActions]]
Xstds = [np.std(x) for x in [deltaP, nVel, nVel, validActions]]
Tmean = [meanRein]
Tstd = [stdRein]
####################
#SPECIFIC ML VARS:
####################

framesPerTrial = 25
nTrials = 5000

nHidden = [25]
n_epochs = 400
learningRate = 0.05

Epsilon = 1.
finalEpsilon = 0.0001
epsilon_decay =  np.exp(np.log(finalEpsilon) / nTrials)
gamma = 0.8

expectedState = ["deltaP", "bobberNormalizedVel", "fishNormalizedVel"]
n_inputs =  len( expectedState) + 1 #add 1 to the expected state for the action.
DQN = None
####################

##########
# Misc:
###########

resetScenePerTrial = True

averageNTrialSplits = 10 # split the trials into 15 for the average range (ie if nTrials = 2500; 2500 * (1/15) = ceiling(166.66667); )
avgNTrialsRange = nTrials // averageNTrialSplits
doDebug = False


def runFrameByFrame(JPC):
    print("running %s total frames" % (nTrials * framesPerTrial))
    print("ExperimentArgs:")
    print(framesPerTrial, nTrials, nHidden, n_epochs, learningRate, gamma,sep='\n')
    FramesToPlay = framesPerTrial * nTrials
    trialTracker = 0

    debug()

    X = np.zeros((framesPerTrial, DQN.n_inputs))
    R = np.zeros((framesPerTrial, 1))
    Qn = np.zeros((framesPerTrial, 1))

    r_sum = 0
    r_last_2 = 0
    epsilon=Epsilon 

    frameCount = 1
    msgToSend = 10

    arrr = JPC.recvStr()
    initStateStr = arrr[1:-1].split(',');
    initState = list([int(val.split(':')[-1]) for val in initStateStr])
    s = initState
    a, _ign = DQN.EpsilonGreedyUse(s)

    meanRein = []
    pastStateActions = []

    resetMsg = 5

    while(frameCount <= FramesToPlay):
        JPC.sendInt(msgToSend)
        if(msgToSend==resetMsg):
            nState = JPC.recvStr()[1:-1].split(',');
            nState = list([int(val.split(':')[-1]) for val in nState])
            s = nState
            a, _ign = DQN.EpsilonGreedyUse(s)

        step = (frameCount-1) % framesPerTrial
        #make sure that the frame has processed:
        allGood = JPC.recvInt()
        if(allGood != 10):
            raise Exception("Java encountered an error")

        #get the state:
        stateStr = JPC.recvStr()
        #################
        # MAIN LOOP
        #################
        
        #state is in the formate <deltaP, deltaV>
        state = stateStr[1:-1].split(',')
        state = list([int(val.split(':')[-1]) for val in state])
        sn = state

        rn = DQN.getReinforcement(state)    # Calculate resulting reinforcement
        an, qn = DQN.EpsilonGreedyUse(state)  # choose next action
        X[step, :] = np.hstack((s, a))
        R[step, 0] = rn
        Qn[step, 0] = qn
        s, a = sn, an

        stateAction = s + [a]
        pastStateActions.append(stateAction)

        debug("frame %d of Trial %d current state: %s" % (frameCount, trialTracker, stateStr))
        debug("reinforcement: " + str(rn))
        debug("taking action: " + str(a))
        debug("-----")
        
        #tell java to make this action:
        JPC.sendInt(int(a))


        #######
        # End trial:
        #######
        if((frameCount)%framesPerTrial==0):
            
            trialTracker += 1

            T = R + gamma * Qn
            curSome = np.sum(R)
            r_sum += curSome

            meanRein.append(curSome / len(R))

            if trialTracker > nTrials - 3:
                r_last_2 += curSome
           
            epsilon *= epsilon_decay
            DQN.train(X, T, n_epochs, learningRate, method='sgd', verbose=False)

            #Reset trackers:
            X = np.zeros((framesPerTrial, DQN.n_inputs))
            R = np.zeros((framesPerTrial, 1))
            Qn = np.zeros((framesPerTrial, 1))


            if(resetScenePerTrial):
                msgToSend = resetMsg
                s = initState
                a, _ign = DQN.EpsilonGreedyUse(s)


        else:
            msgToSend = 10
        #################
        frameCount += 1
    dumpDir = os.path.join(myDir, "DQN.dump")
    DQN.dump(dumpDir)
    
    savePlot(meanRein)

    R = r_sum / (nTrials * framesPerTrial)
    R_last2 = r_last_2 / (2 * framesPerTrial)
    saveLastNActionStatePairs(20,pastStateActions)
    saveResults(R, R_last2)


    JPC.sendInt(0)
    return R, R_last2


def saveResults(R, R_last2):
    toSave = "results.csv"
    out = os.path.join(myDir,toSave)
    data = [[nTrials, framesPerTrial, n_epochs, nHidden, gamma, learningRate, R, R_last2]]
    df = pds.DataFrame(data, columns=["NTrials", "frames/trial", "n_epochs", "hidden layers", "gamma", "learning rate", "R", "R last 2"])
    df.to_csv(out)


def saveLastNActionStatePairs(nToSave, actionStatePairs):
    toSave = "ActionState.csv"
    out = os.path.join(myDir,toSave)
    df = pds.DataFrame(actionStatePairs[-nToSave:], columns = ["deltaP", "bobber normal vel", "fish normal vel", "action taken"])
    df.to_csv(out)


def savePlot(meanReinforcements):
    toSave = "meanReinByTrial.png"
    out = os.path.join(myDir, toSave)

    meanReinforcements = np.array(meanReinforcements)

    nAverages = np.array(np.array_split(meanReinforcements, averageNTrialSplits)).T
    positions = [(avgNTrialsRange/2) + (avgNTrialsRange * i) for i in range(averageNTrialSplits)]

    plt.boxplot(nAverages, positions=positions, widths=1, manage_ticks=False)
    plt.plot(range(1, len(meanReinforcements)+1), meanReinforcements, alpha=0.5)

    binSize = 20
    smoothed = np.mean(meanReinforcements.reshape((int(nTrials / binSize), binSize)), axis=1)
    plt.plot(np.arange(1, 1 + int(nTrials / binSize)) * binSize, smoothed)

    nTicks = 10
    tickIncrement = nTrials / nTicks

    plt.xticks(np.arange(1,len(meanReinforcements)+100,tickIncrement))
    plt.savefig(out)






def main(expIndex=None, expDir=expDir):
    global framesPerTrial, nTrials, n_epochs, learningRate, gamma, DQN, nHidden, myDir
    if(expIndex!=None):
        tempPath = os.path.join(expDir, expNtmp%expIndex)
        debug(tempPath)
        myDir = Path(tempPath)

        debug("Loading experiment %s"%expIndex)

        expCSV = os.path.join(expDir, ExperimentsCSV)
        expDF = pds.read_csv(expCSV,index_col=0)
        expr = expDF.iloc[expIndex]

        framesPerTrial = expr["framesPerTrial"]
        nTrials = expr["nTrials"]
        nHidden = [int(varr) for varr in expr["nHiddens"][1:-1].split(',')]
        n_epochs = expr["n_epochs"]
        learningRate = expr["learningRate"]
        gamma = expr["gamma"]

        debug(expr)
    
    #do the plotting setup:
    ax = plt.figure(figsize=(15,5)).gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ylim([-1,4])
    plt.grid()
    plt.xlabel("Trial (Time)")
    plt.ylabel("Mean Reinforcement")

    myDir.mkdir(parents=True, exist_ok=True)

    JPC = JPComms.JPComms(modesExcpected["TRAIN"])

    DQN = RLNN.RLNeuralNetwork(validActions, Epsilon, n_inputs, nHidden, 1)
    DQN.createStandards(Xmeans, Xstds, Tmean, Tstd)

    debug("\n-----------------------------------------------------")
    r, rLast2 = runFrameByFrame(JPC)


def debug(*toPrint, sep=" "):
    if(doDebug):
        print(*toPrint, sep=sep)

if __name__ == "__main__":
    expIndex = None
    if(len(sys.argv)==2):
        try:
            expIndex = int(sys.argv[1])
        except ValueError:
            raise ValueError("Expected argument to be of type int.")

    elif(len(sys.argv) > 2):
        raise Exception("Only one argument can be supplied.")

    main(expIndex, expDir)