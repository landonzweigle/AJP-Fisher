from os import sep
import RLNN, math, sys
import JavaPythonComms as JPComms

from numpy.core.defchararray import split
import numpy as np, pandas as pds

modesExcpected = {"TRAIN": ("FrameAtTime", "SafePractice"),"TEST": ("PersonPlay", "Practice"),"NORMAL": ("PersonPlay", "Normal")}
ExperimentsCSV = "../Experiments/experiments.csv"

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

Xmeans = [meanH, meanV, meanAct]
Xstds = [stdH, stdV, stdAct]
Tmean = [meanRein]
Tstd = [stdRein]
####################
#SPECIFIC ML VARS:
####################

framesPerTrial = 200 #amount in frames
nTrials = 100

nHidden = [100]
n_epochs = 50
learningRate = 0.01

Epsilon = 1.
finalEpsilon = 0.0001
epsilon_decay =  np.exp(np.log(finalEpsilon) / nTrials)
gamma = 0.8


n_inputs = 3 #{deltaP, deltaV, action}
DQN = None
####################




def runFrameByFrame(JPC):
    print("ExperimentArgs:")
    print(framesPerTrial, nTrials, nHidden, n_epochs, learningRate, gamma,sep='\n')
    FramesToPlay = framesPerTrial * nTrials
    trialTracker = 0

    print()

    X = np.zeros((framesPerTrial, DQN.n_inputs))
    R = np.zeros((framesPerTrial, 1))
    Qn = np.zeros((framesPerTrial, 1))

    r_sum = 0
    r_last_2 = 0
    epsilon=Epsilon 

    frameCount = 1
    msgToSend = 10
    while(frameCount <= FramesToPlay):
        JPC.sendInt(msgToSend)

        #make sure that the frame has processed:
        allGood = JPC.recvInt()
        if(allGood != 10):
            raise Exception("Java encountered an error")

        #get the state:
        stateStr = JPC.recvStr()
        print("frame %s current state: %s" % (frameCount, stateStr))
        
        #################
        # MAIN LOOP
        #################
        
        #state is in the formate <deltaP, deltaV>
        state = stateStr[1:-1].split(',')
        state = list([int(val.split(':')[-1]) for val in state])
        s = state
        print("converted state:", state)
        # s,a = state

        step = frameCount % framesPerTrial
        # sn = next_state_f(s, a)        # Update state, sn, from s and a
        rn = DQN.getReinforcement(state)    # Calculate resulting reinforcement
        a, qn = DQN.EpsilonGreedyUse(state)  # choose next action
        X[step, :] = s + [a]
        R[step, 0] = rn
        Qn[step, 0] = qn
        
        #tell java to make this action:
        print("taking action: " + str(a))
        JPC.sendInt(int(a))


        #######
        # End trial:
        #######
        if((frameCount)%framesPerTrial==0):
            
            trialTracker += 1

            T = R + gamma * Qn
            r_sum += np.sum(R)
            if trialTracker > nTrials - 3:
                r_last_2 += np.sum(R)
           
            epsilon *= epsilon_decay
            DQN.train(X, R + gamma * Qn, n_epochs, learningRate, method='sgd', verbose=False)

            #Reset trackers:
            X = np.zeros((framesPerTrial, DQN.n_inputs))
            R = np.zeros((framesPerTrial, 1))
            Qn = np.zeros((framesPerTrial, 1))


            msgToSend = 5
        else:
            msgToSend = 10


        
        #################
        frameCount += 1

    JPC.sendInt(0)
    return r_sum / (nTrials * framesPerTrial), r_last_2 / (2 * framesPerTrial)









def main():
    global framesPerTrial, nTrials, n_epochs, learningRate, gamma, DQN, nHidden


    if(len(sys.argv)==2):
        try:
            fileToLoad = int(sys.argv[1])
        except ValueError:
            raise ValueError("Expected argument to be of type int.")
        print("Loading experiment %s"%fileToLoad)
    elif(len(sys.argv) > 2):
        raise Exception("Only one argument can be supplied.")

    expDF = pds.read_csv(ExperimentsCSV,index_col=0)
    expr = expDF.iloc[fileToLoad]

    #framesPerTrial, nTrials, n_epochs, learningRate, gamma
    framesPerTrial = expr["framesPerTrial"]
    nTrials = expr["nTrials"]
    n_epochs = expr["n_epochs"]
    learningRate = expr["learningRate"]
    gamma = expr["gamma"]

    nHidden = [int(varr) for varr in expr["nHiddens"][1:-1].split(',')]
    
    print(expDF)
    print(expr)
    print()

    JPC = JPComms.JPComms(modesExcpected["TRAIN"])

    DQN = RLNN.RLNeuralNetwork(validActions, Epsilon, n_inputs, nHidden, 1)
    DQN.createStandards(Xmeans, Xstds, Tmean, Tstd)

    print("\n-----------------------------------------------------")
    r, rLast2 = runFrameByFrame(JPC)


if __name__ == "__main__":
    main()
    

