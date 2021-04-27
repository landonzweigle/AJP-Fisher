import socket, RLNN, math, time
from typing import MappingView

from numpy.core.defchararray import split
import numpy as np, pandas as pds

modesExcpected = {"TRAIN": ("FrameAtTime", "SafePractice"),"TEST": ("PersonPlay", "Practice"),"NORMAL": ("PersonPlay", "Normal")}

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

n_epochs = 50
learningRate = 0.01

Epsilon = 1.
finalEpsilon = 0.0001
epsilon_decay =  np.exp(np.log(finalEpsilon) / nTrials)
gamma = 0.8


n_inputs = 3 #{deltaP, deltaV, action}
DQN = RLNN.RLNeuralNetwork(validActions, Epsilon, n_inputs, [100], 1)
DQN.createStandards(Xmeans, Xstds, Tmean, Tstd)
####################





class JPComms:
    CNN_ATMPTS = 10
    sock = None    
    framemode = None
    gamemode = None


    def __init__(self, mode):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.framemode, self.gamemode = mode
        
        trysLeft = self.CNN_ATMPTS
        connected = False
        lastExep = None
        while(trysLeft > 0 and not connected):
            try:
                self.sock.connect(("localhost",13337))
                connected = True
            except Exception as e:
                lastExep = e
                trysLeft -= 1

                if(trysLeft > 0):
                    time.sleep(0.25)
                else:
                    print("Ran out of connection attempts")
                    raise lastExep


        self.startupSeq()



    def startupSeq(self):
        firstMsg = self.recvStr()
        print("FM: " + firstMsg)
        if(firstMsg=="Hello Python :)"):
            self.sendStr("Hello Java :D")
            #recv expected framemode and gamemode:
            print("Getting modes")
            actFrameMode = self.recvStr()
            actGameMode = self.recvStr()
            print("modes: " + actFrameMode + " " + actGameMode)
            print("Checking modes")
            if ( (actFrameMode != self.framemode) or (actGameMode != self.gamemode) ):
                self.sendStr("MMM")
                raise Exception("modes dont match")
            self.sendStr("")
            print("\"HandShake\" successful")
            return
            
    def sendInt(self, toSend):
        self.sock.sendall(toSend.to_bytes(4, 'big'))
            
    def recvInt(self):
        intBytes = self.sock.recv(4)
        return int.from_bytes(intBytes, 'big')

    def sendStr(self, toSend):
        if(type(toSend)==str):

            enc = toSend.encode('utf-8')
            msgLen = len(enc)
            self.sock.sendall(msgLen.to_bytes(4, 'big')) #send message length
            self.sock.sendall(enc) #send Message.
        

    def recvStr(self):
        if(not self.sock):
            return -1
        msgLen = int.from_bytes(self.sock.recv(4),'big')

        msg = self.sock.recv(msgLen)
        return msg.decode('utf-8')
        








def runFrameByFrame(JPC):
    FramesToPlay = framesPerTrial * nTrials
    trialTracker = 0


    X = np.zeros((framesPerTrial, DQN.n_inputs))
    R = np.zeros((framesPerTrial, 1))
    Qn = np.zeros((framesPerTrial, 1))

    # s = initial_state_f()
    # a, _ = DQN.EpsilonGreedyUse(DQN, s, validActions, epsilon)

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
    JPC = JPComms(modesExcpected["TRAIN"])
    print("\n-----------------------------------------------------")
    r, rLast2 = runFrameByFrame(JPC)


if __name__ == "__main__":
    main()
    

