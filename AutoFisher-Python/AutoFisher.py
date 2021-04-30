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
doDebug = False



def sampleSTD(values, avg):
    sqrSum = sum([(val - avg)**2 for val in values])
    div = sqrSum / (len(values) - 1)
    return math.sqrt(div)

minH = 35
maxH = 687
meanH = (minH+maxH)/2
stdH = sampleSTD([minH,maxH], meanH)

minV = -1000
maxV = 1000
meanV = (minV + maxV)/2
stdV = sampleSTD([minV, maxV], meanV)

validActions = [0,1] #[reel out, reel in]
meanAct = 0.5
stdAct = 0.5

reinforcements = [0,1,2,3]
meanRein = 1.5
stdRein = 1.118

Xmeans = [meanH, meanH, meanV, meanV, meanAct]
Xstds = [stdH, stdH, stdV, stdV, stdAct]
Tmean = [meanRein]
Tstd = [stdRein]
####################
#SPECIFIC ML VARS:
####################

framesPerTrial = 10 #amount in frames
nTrials = 5

nHidden = [100]
n_epochs = 50
learningRate = 0.01

Epsilon = 1.
finalEpsilon = 0.0001
epsilon_decay =  np.exp(np.log(finalEpsilon) / nTrials)
gamma = 0.8


n_inputs = 5 #{deltaP, deltaV, action} or {bobberPos, fishPos, bobberVel, fishVel, action}
DQN = None
####################




def runFrameByFrame(JPC):
    debug("ExperimentArgs:")
    debug(framesPerTrial, nTrials, nHidden, n_epochs, learningRate, gamma,sep='\n')
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

    initStateStr = JPC.recvStr()[1:-1].split(',');
    initState = list([int(val.split(':')[-1]) for val in initStateStr])
    s = initState
    a, _ign = DQN.EpsilonGreedyUse(s)

    meanRein = []
    pastStateActions = []

    while(frameCount <= FramesToPlay):
        JPC.sendInt(msgToSend)

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

        step = frameCount % framesPerTrial
        # sn = next_state_f(s, a)        # Update state, sn, from s and a
        rn = DQN.getReinforcement(state)    # Calculate resulting reinforcement
        an, qn = DQN.EpsilonGreedyUse(state)  # choose next action
        X[step, :] = s + [a]
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


            msgToSend = 5
            s = initState
            a, _ign = DQN.EpsilonGreedyUse(s)

        else:
            msgToSend = 10
        #################
        frameCount += 1
    dumpDir = os.path.join(myDir, "DQN.dump")
    DQN.dump(dumpDir)

    R = r_sum / (nTrials * framesPerTrial)
    R_last2 = r_last_2 / (2 * framesPerTrial)
    saveLastNActionStatePairs(20,pastStateActions)
    saveResults(R, R_last2)
    savePlot(meanRein)

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
    df = pds.DataFrame(actionStatePairs[-nToSave:], columns = ["bobber pos", "fish pos", "bobber vel", "fish vel", "action taken"])
    df.to_csv(out)

def savePlot(meanReinforcements):
    print(meanReinforcements)
    toSave = "meanReinByTrial.png"
    out = os.path.join(myDir, toSave)

    ax = plt.figure().gca()
    plt.ylim([0,4])
    plt.grid()

    plt.plot(meanReinforcements)
    plt.xlabel("Trial")
    plt.ylabel("Mean Reinforcement")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

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
    
    myDir.mkdir(parents=True, exist_ok=True)

    JPC = JPComms.JPComms(modesExcpected["TRAIN"])

    DQN = RLNN.RLNeuralNetwork(validActions, Epsilon, n_inputs, nHidden, 1)
    DQN.createStandards(Xmeans, Xstds, Tmean, Tstd)

    debug("\n-----------------------------------------------------")
    r, rLast2 = runFrameByFrame(JPC)

def debug(*toPrint, sep=" "):
    if(doDebug):
        print(toPrint, sep=sep)

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