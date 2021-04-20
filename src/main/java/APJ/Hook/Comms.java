package APJ.Hook;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;

import APJ.Fisher.FishGame;

public class Comms extends Thread{
	public static Comms singleton;
	
	public final int port = 13337;
	ServerSocket listener;
	
	DataInputStream dIn;
	DataOutputStream dOut;
	
	public Comms() throws Exception {
		if(singleton!=null)
			throw new Exception("multiple instances of Comms found.");
		else 
			singleton = this;
		
		this.listener = new ServerSocket(port);
	}
	
	public void run() {
		try {
			Socket sock = this.listener.accept(); //One this executes we the connection has successfully been made with the python prog.

			this.dIn = new DataInputStream(sock.getInputStream());
			this.dOut = new DataOutputStream(sock.getOutputStream());
			
//			Integer toWrite = 12345678;
//			this.dOut.write(toWrite); //This works if I have a very large bytes to recieve on python...?			
//			byte[] bytes = ByteBuffer.allocate(4).putInt(1234567876).array();
//			this.dOut.write(bytes);
			//This is a weird start-up sequence ¯\_(ツ)_/¯
			
			byte[] msgToSend = "Hello python :)".getBytes();
			this.dOut.write(msgToSend);
			
			byte[] inBytes = this.dIn.readAllBytes();
			String inMsg = new String(inBytes);

			FishGame.print(inMsg);

			if(inMsg.equals("Hello Java :D")) {
				FishGame.startGame(); //Start the game.				
			}
			
			
			
			
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
}
