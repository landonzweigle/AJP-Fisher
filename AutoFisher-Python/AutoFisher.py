import socket
recvSize = 2048 * 16

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost",13337))

    firstMsg = sock.recv(4)
    print("bytes: %s" % firstMsg)
    print(int.from_bytes(firstMsg, 'big'))

    firstMsg = sock.recv(64)
    print("bytes: %s" % firstMsg)
    msgDec =firstMsg.decode('utf-8') 
    print(msgDec)

    if(msgDec=="Hello python :)"):
        print("WOO!!")
        sock.sendall("Hello Java :D".encode('utf-8'))
        

if __name__ == "__main__":
    main()
    

