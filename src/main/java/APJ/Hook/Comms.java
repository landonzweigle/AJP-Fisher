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
		
		boolean colliding;
		
		int bobberPos;
		int bobberVel;
		
		int fishPos;
		int fishVel;
		
		int deltaP;
		int deltaV;
		
		//deltaX: the vector from bobber.posY to fish.posY.
		//deltaX: the vector from bobber.velY to fish.velY.
		public GameState(int bobberPos, int fishPos, int bobberVel, int fishVel, boolean colliding) { 
			this.bobberPos = bobberPos;
			this.bobberVel = bobberVel;
			
			this.fishPos = fishPos;
			this.fishVel = fishVel;
			
			this.colliding = colliding;
			
			this.deltaP = fishPos - bobberPos;
			this.deltaV = fishVel - bobberVel;
		}
		
//		This is what is ultimately sent to python as the state.
		public String toString() {
			
			int bobberSimVel = (bobberVel!=0)? bobberVel / Math.abs(bobberVel) : 0; //normalized bobber velocity
			int fishSimVel   =  (fishVel!=0) ?  fishVel  /  Math.abs(fishVel)  : 0; //normalized fish velocity

			int nDeltaP = (deltaP!=0) ? deltaP / Math.abs(deltaP) : 0;
			nDeltaP = (this.colliding) ? 0 : nDeltaP;
			
			int col = (colliding==true)? 1 : 0;
			
			String _ret = "<bP: %s, fP: %s, bSV: %s, fSV: %s, col: %s>";
			_ret = String.format(_ret, this.bobberPos, this.fishPos, bobberSimVel, fishSimVel, col);
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
				FishGame.startGame(true); //Start the game.	
				FrameByFramePlayGame();
				FishGame.stopPlaying();
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
		GameState initState = getGameState();
		sendStr(initState.toString());
		
		FishGame.nextFrame();
		while((recvMsg=recvInt())!=0) {
			if(recvMsg==10) {}else if(recvMsg==5) {
				FishGame.startGame(true);
				initState = getGameState();
				sendStr(initState.toString());
				FishGame.nextFrame();
			}
			//Wait until frame processed:
			while(!FishGame.isFrameProccessed()) {}
			
			//tell python the frame has been processed:
			sendInt(10);
			
			GameState curState = getGameState();
			
			String state = curState.toString();
			sendStr(state);
			//Get the next action from python:
			int action = recvInt();
			boolean reelIn = (action==0)?false:(action==1)?true:null;
			
			FishGame.setReelIn(reelIn);
			
			FishGame.nextFrame();
		}
		FishGame.print("Python ended");
	}
	
	
	public GameState getGameState() {
		Sprite CA = FishGame.CA;
		Sprite Fish = FishGame.fish;
		
		
		
		GameState _ret = new GameState((int)CA.getY(), (int)Fish.getY(), (int)CA.getyVel(), (int)Fish.getyVel(), Fish.collidingWith(CA));
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
