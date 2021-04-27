package APJ.Hook;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;

import APJ.Fisher.FishGame;
import APJ.Fisher.Sprite;

public class Comms extends Thread{
	class GameState{
		int deltaP;
		int deltaV;
		
		//deltaX: the vector from bobber.posY to fish.posY.
		//deltaX: the vector from bobber.velY to fish.velY.
		public GameState(int deltaP, int deltaV) { 
			this.deltaP = deltaP;
			this.deltaV = deltaV;
		}
		
		public String toString() {
			String _ret = "<deltaP: %s, deltaV: %s>";
			_ret = String.format(_ret, this.deltaP, this.deltaV);
			return _ret;
		}
	}
//	Integer toWrite = 12345678;
//	this.dOut.write(toWrite); //This works if I have a very large bytes to recieve on python...?			
//	byte[] bytes = ByteBuffer.allocate(4).putInt(1234567876).array();
//	this.dOut.write(bytes);
	
	
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
		
			
			//This is a weird start-up sequence ¯\_(ツ)_/¯
			sendStr("Hello Python :)");
			FishGame.print("Getting msg");
			String inMsg = recvStr();

			FishGame.print(inMsg);

			if(inMsg.equals("Hello Java :D")) {
				FishGame.print("Checking game modes...");
				String framemode = FishGame.framemode.name(); 
				String gamemode = FishGame.gamemode.name();
				
				String mismatchedMode = "MMM";
				
				sendStr(framemode);
				sendStr(gamemode);
				String expectedMode  = recvStr();
				
				if(expectedMode.equals(mismatchedMode)) {
					FishGame.print("GameModes do not match.");
					sock.close();
					System.exit(1);
				}else if(expectedMode.isEmpty()){
					FishGame.print("GameModes match!");
				}
				
				FishGame.print("Starting game...\n");
				FishGame.startGame(); //Start the game.	
				FrameByFramePlayGame();
			}else {
				FishGame.print("Startup message didn't match :(");
				return;
			}
		} catch (Exception e) {
			FishGame.stopPlaying();
			e.printStackTrace();
		}
	}
	
	// a loop looks like this:
	//if(condition from python):
	//Tell python the state.
	//Step FishGame to next frame.
	//repeat.	
	private void FrameByFramePlayGame() throws Exception {	
		int recvMsg;
		while((recvMsg=recvInt())!=0) {
			if(recvMsg==10) {}else if(recvMsg==5) {
				FishGame.startGame();
			}
			//Wait until frame processed:
			while(!FishGame.isFrameProccessed()) {}
			
			//tell python the frame has been processed:
			sendInt(10);
			
			GameState curState = getGameState();
			//For communicating our state to python we have several options:
			//Send curState.toString to python.
			//or
			//Send several integers.
			  
			//Pros and cons:
			//Pro for sending string:
			//Very flexible.
			//Con for sending String:
			//Might take longer because of more data.
			//Yeah lets just go with sending the string. If it proves too slow we can change it.
			
			
			String state = curState.toString();
			sendStr(state);
			//Get the next action from python:
			int action = recvInt();
			boolean reelIn = (action==0)?false:(action==1)?true:null;
			
			FishGame.setReelIn(reelIn);
			
			FishGame.nextFrame();
		}
	}
	
	
	public GameState getGameState() {
		Sprite CA = FishGame.CA;
		Sprite Fish = FishGame.fish;
		
		//vector is defined as: target - origin.
		GameState _ret = new GameState((int)(Fish.getY() - CA.getY()), (int)(Fish.getyVel() - CA.getyVel()));
		return _ret;		
	}
	
	private void sendInt(Integer toSend) throws IOException {
		byte[] bytes = ByteBuffer.allocate(4).putInt(toSend).array();
		this.dOut.write(bytes);
	}
	
	private int recvInt() throws IOException {
		Integer _ret = this.dIn.readInt();
		return _ret;
	}
	
	private void sendStr(String toSend) throws IOException {
		byte[] msg = toSend.getBytes();
		byte[] len = ByteBuffer.allocate(4).putInt(msg.length).array();
		
		this.dOut.write(len);
		this.dOut.write(msg);
	}
	
	private String recvStr() throws IOException {
		
		Integer msgLen = this.dIn.readInt();
		byte[] msgBytes = new byte[msgLen];
		
		
		this.dIn.readFully(msgBytes, 0, msgLen);
		String inMsg = new String(msgBytes);
		return inMsg;
	}
	
	
}
