import socket, time

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
                    #print("Ran out of connection attempts")
                    raise lastExep
        self.startupSeq()



    def startupSeq(self):
        firstMsg = self.recvStr()
        #print("FM: " + firstMsg)
        if(firstMsg=="Hello Python :)"):
            self.sendStr("Hello Java :D")
            #recv expected framemode and gamemode:
            #print("Getting modes")
            actFrameMode = self.recvStr()
            actGameMode = self.recvStr()
            #print("modes: " + actFrameMode + " " + actGameMode)
            #print("Checking modes")
            if ( (actFrameMode != self.framemode) or (actGameMode != self.gamemode) ):
                self.sendStr("MMM")
                raise Exception("modes dont match")
            self.sendStr("")
            #print("\"HandShake\" successful")
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
