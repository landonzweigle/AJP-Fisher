import socket
modesExcpected = {"TRAIN": ("FrameAtTime", "SafePractice"),"TEST": ("PersonPlay", "Practice"),"NORMAL": ("PersonPlay", "Normal")}
FramesToPlay = 2000


class JPComms:
    sock = None    
    framemode = None
    gamemode = None


    def __init__(self, mode):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("localhost",13337))

        self.framemode, self.gamemode = mode

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
    frameCount = 1
    while(frameCount <= FramesToPlay):
        JPC.sendInt(10)

        #make sure that the frame has processed:
        allGood = JPC.recvInt()
        if(allGood != 10):
            raise Exception("Java encountered an error")

        #get the state:
        state = JPC.recvStr()
        print("frame %s current state: %s" % (frameCount, state))

        frameCount += 1
        #input("please press enter to continue")

    JPC.sendInt(0) #OH NO, WHAT DO I SEND??? I KNOW IT JUST HAS TO BE DIFFERENT THAN 10 BUT THAT STILL LEAVES AN INFINITE AMOUNT OF NUMBERRRSSSS AHHHHHH NOOOOO IM DROWWWNNNIIIINNNGGG  

def main():
    JPC = JPComms(modesExcpected["TRAIN"])

    runFrameByFrame(JPC)


if __name__ == "__main__":
    main()
    

