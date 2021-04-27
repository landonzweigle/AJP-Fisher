package APJ.Fisher;


import java.net.URL;
import java.util.Scanner;

import APJ.Hook.Comms;
import javafx.application.Application;

import javafx.animation.AnimationTimer;
import javafx.geometry.VPos;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.image.Image;
import javafx.scene.input.MouseButton;
import javafx.scene.media.AudioClip;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.TextAlignment;
import javafx.stage.Stage;

public class FishGame extends Application {

	/*
	 * Definitions: Mode_Idle_out = time when the player has the line casted out
	 * (click to pull line, if not in Leniate_period, mode changes to Mode_Idle_in).
	 * Mode_Idle_in = time when the player has the line in (nothing is happening at
	 * all, just the background is animating). When the Wait_Time is reached, the
	 * Leniate_Period begins and a noise is played. Mode_Base = time when the fish,
	 * capture area, capture bar, and frame are displayed (player attempts to
	 * capture fish here) background animation stops. Leniate_period = time when the
	 * player hears the sound that they have a fish hooked (must click within 'x'
	 * amount of seconds. if they miss this period another random wait_time is
	 * generated again.) Wait_time = time required to wait, from the begining of
	 * Idle_out to the begining off the Leniate_period. Case_Win = if the user
	 * captures the fish, the Mode_Base display disapears and the fish that they
	 * captured is displayed and they are awarded the fish (wait for click to go to
	 * Mode_idle_in). Case_Lose: if the user loses the fish, the Base_mode display
	 * disapears and mode is set to Mode_Idle_in.
	 */

	// ---------------VARIABLES---------------//

// Physics stuff (all constants or canstantly changing).

	static Scanner input = new Scanner(System.in);
	// Time of last frame.
	public static double lastTime = System.nanoTime();
	// The Capture areas gravity rate.
	public static double GRAV = -2500; //base is -4000
	// Acceleration rate.
	public static double MOTOR = 3500; //base is 5000
	// Fishes max speed.
	public static double MAXSPEED = 1000;
	// fishes min speed.
	public static double MINSPEED = -1000;
	// Rate that the bar raises.
	public static double CAPRATEUP = 25;
	// rate the bar lowers.
	public static double CAPRATEDOWN = 50;
	// the time required to change fishes direction
	public static double ttc;
	// The last time of the frame.
	public static double lt = System.currentTimeMillis();
	// rate the fish slows down.
	public static double DECRATE = 75;
	// Fish minimum speed.
	public static double MINFISH = 10;
	// Fish max speed.
	public static double MAXFISH = 2500;
	// Determines if player is clicking (for the animation loop).
	public static boolean isClicked = false;
	// Points required to capture fish.
	public static double CAPTUREPOINTS = 100;
	// Highest y value of the bar.
	public static double CAPHEIGHT = 660;
	// Height of the capture area.
	public static int CA_HEIGHT = 150;
	// The idle background
	public static Image IDLE;
	// The minigame framework.
	public static Image MINIGAME;
	// the randomly generated number for the fish.
	public static int fishNum;
	// Time required to wait to catch the fish.
	public static double waitTime;
	// All the fish.
	public static Fish ourFish = new Fish();
	// array of images that makes the animation for the player casting a line.
	public static Image[] castAnim;
	// 2D array of the positions for the fish when he is pulled out of the water.
	public static int[][] bobberPos = new int[][] { { 576, 371 }, { 526, 226 }, { 269, 166 }, { 146, 240 } };
	// Image display for winning a fish.
	public static Image FISHWON;
	// Image display for losing a fish.
	public static Image FISHLOSE;
	// Time between frames for the animation.
	public static Image GAMEOVER;
	// This is the image for when you lose the game.
	public static double frameRate = 175;
	// the next time (in milliseconds) that the next frame will play.
	public static double animTime = 0;
	// the index for the frame of the animation.
	public static int animPos = 0;
	// amount of fish lost.
	public static int fishLost = 0;
	// amount of fish caught.
	public static int fishCaught = 0;
	// true if the sound hasnt played yet, false if otherwise (so the sound
	// doesn'trepeat).
	public static boolean firstNoise = true;
	// Current max wait time (reaction based portion).
	public static double maxWaitTime = 0.0;
	// how long the fish will stay on the hook before the fish runs away.
	public static double MAXWAITTIMEHOLD = 750.0;
	// Fish of the image you are trying to catch.
	public static Image fishImage;
	// scaled version of the fish.
	public static Image scaledFish;
	// The fish's name
	public static String fishName = "OH NO, I'M BURNING!!! I'M BUURRRNIIINNNGG!!!1!!!1 \n Something went wrong :P";
	// maditory wait time.
	public double manditoryWait = 1000.0;
	// manditory wait time added to the current time (later on).
	public static double actualManditoryWait = 0.0;

	// position to display the name
	public static int[] namePos = new int[] { 769, 400 };
	// positino to display the difficulty.
	public static int[] difPos = new int[] { 769, 551 };
	// The record amount of fish that have ever been caught.
	public static int recordFish = 0;
	// Whether or not the amount of caught fish beats the old record
	public static boolean isRecord = false;
// End Physics stuff.

// Begin Variables to be changed per gamemode change (essentially whenever Mode_Idle_out)

	// The capture area.
	public static Sprite CA = new Sprite();
	// The fish
	public static Sprite fish = new Sprite();
	// The bar
	public static Image bar;
	// players current points (to capture fish).
	public static double myPoints = 50;
	// from 1 and up (recommended to be less than 10) Difficulty of fish.
	public static int difficulty = 7;

	public static boolean canPlay = false;
	
	private static volatile boolean reelIn = false;
	
	
	// The current mode of the game (see full definitions above)
	// -1 = Mode_idle_int.
	// 0 = Mode_idle_out.
	// 1 = Mode_Base.
	// 2 = Mode_Win
	// 3 = Mode_Lose.
	// 4 = Game Over.
	public static int mode = -1;

	static String[] args;

	static double lastFPS = 0;
	static double[] dtInfo = new double[10]; // hold the last 10 delta times.
	static int dtiIndex = 0;
	static int frameCount = 0;

	
	
	public enum FrameMode{
		PersonPlay,   //The "regular" game (this version still has stuff removed.)
		FrameAtTime,  //For training a model. Waits until a specified even to process the next frame.
	}
	
	public enum GameMode{
		Normal,       //The "regular" game (this version still has stuff removed.)
		SafePractice, //You cannot lose a fish and there is no intermediate state of casting/etc. Once a fish is caught a new fish is generated. (the game starts with a cought fish)
		Practice      //Like SafePractice but you can lose fish. Once a fish is lost a new fish is generated.
	}
	
	
	
	
	static final boolean useComms = false;
	
	public static final FrameMode framemode = FrameMode.PersonPlay;
	public static final GameMode gamemode = GameMode.SafePractice;
	
	private static volatile boolean precedFrame = false; // Set to true to proceed to the next frame in gamemode FrameAtTime.
	public static volatile boolean frameProccessed = true;
	
	
	
	
	public static synchronized void setReelIn(boolean shouldReelIn) {
		reelIn = shouldReelIn;
	}
	
	public static synchronized void nextFrame() {
		precedFrame = true;
		frameProccessed = false;
	}
	
	public static synchronized boolean isFrameProccessed() {
		return frameProccessed;
	}
	
// End changed variables.

	// Landon Zweigle
	// Used whenever we need to reset the sprites.
	// Parameters: none
	// Returns: none.
	public static void startGame() {
		// Set the images.
		FISHLOSE = new Image(ClassLoader.getSystemClassLoader().getResource("You Lost the Fish0.png").toString(), 1280,
				720, true, false);
		FISHWON = new Image(ClassLoader.getSystemClassLoader().getResource("Capture Screen.png").toString(), 1280, 720,
				true, false);
		GAMEOVER = new Image(ClassLoader.getSystemClassLoader().getResource("Game Over0.png").toString(), 1280, 720,
				true, false);
		bar = new Image(ClassLoader.getSystemClassLoader().getResource("bar.png").toString(), 64, 0, false, false);

		castAnim = new Image[] { new Image(ClassLoader.getSystemClassLoader().getResource("Casting0.png").toString()),
				new Image(ClassLoader.getSystemClassLoader().getResource("Casting1.png").toString()),
				new Image(ClassLoader.getSystemClassLoader().getResource("Casting2.png").toString()),
				new Image(ClassLoader.getSystemClassLoader().getResource("Casting3.png").toString()),
				new Image(ClassLoader.getSystemClassLoader().getResource("Casting4.png").toString()) };

		MINIGAME = new Image(ClassLoader.getSystemClassLoader().getResource("Capture Area.png").toString(), 1280, 720,true, false);
		
		IDLE = new Image(ClassLoader.getSystemClassLoader().getResource("Ocean.png").toString(), 1280, 720, true,false);

		
		CA.setImg(new Image(ClassLoader.getSystemClassLoader().getResource("CA.png").toString(), 129, CA_HEIGHT, false, false));
		
		fish.setImg(new Image(ClassLoader.getSystemClassLoader().getResource("fish.png").toString(), 300, 75, true, false));

		int startPos = 560; //They should start together for realism ;)
		
		// Set base Capture area information
		CA.setPos(862, startPos); //OG: 862, -100
		CA.setHeight((int) CA.getImg().getHeight());
		CA.setWidth((int) CA.getImg().getWidth());
		CA.setMaxH(687);
		CA.setMinH(35);

		// Set base fish information
		fish.setPos(852, startPos);
		fish.setHeight((int) fish.getImg().getHeight());
		fish.setWidth((int) fish.getImg().getWidth());
		fish.setMaxH(687);
		fish.setMinH(35);
		canPlay = true;
	}

	public static void launchGame() {
		launch(args);	
	}

	
	

	public static void main(String[] args) throws Exception {
		for(int i=0; i < dtInfo.length; i++) {
			dtInfo[i] = 0;
		}
		
		if (useComms) {
			FishGame.args = args;
			Comms comms = new Comms();
			comms.start();
			
			comms.isAlive();
			while(!canPlay) {
				if(!comms.isAlive()) {
					throw new Exception("comms died while waiting to init.");
				}
			}
			
			if(comms.isAlive()) {
				launchGame();
			}
			
		}else {
			startGame();
			launchGame();
		}
	}

	
	
	// EveryOne
	@Override
	public void start(Stage stage) throws Exception {
		URL location = ClassLoader.getSystemClassLoader().getResource("FishBobberDown.wav");
		AudioClip bobberDown = new AudioClip(location.toString());

		URL locationBK = ClassLoader.getSystemClassLoader().getResource("Ocean Sounds.wav");
		// Credit for audio goes to: https://www.youtube.com/watch?v=xyA5c-ajXyg
		// I edited the audio and made it loopable.
		AudioClip atmosphericSound = new AudioClip(locationBK.toString());

		atmosphericSound.setCycleCount(AudioClip.INDEFINITE);
		atmosphericSound.play(.1);
		// Set stage title
		stage.setTitle("fish game");
		// Instantiate group.
		Group root = new Group();
		// Instantiate the scene.
		Scene sc = new Scene(root);
		// Set the stages scene.
		stage.setScene(sc);
		// Canvas for drawing stuff.
		Canvas can = new Canvas(1280, 720);
		// Instantiate the graphicsContext.
		GraphicsContext gc = can.getGraphicsContext2D();
		gc.drawImage(IDLE, 0, 0);
		// add everything to the console.
		root.getChildren().addAll(can);

		// update the original fish and Capture area.
//		CA.update(0);
//		CA.show(gc);
//		fish.update(0);
//		fish.show(gc);
		animPos = 5;
		
// ---------------------Get Mouse Events-------------------//
		sc.setOnMousePressed(event -> {
			if (event.getButton() == MouseButton.PRIMARY) {
				// if the player is left clicking, set isClicked to true so the fish can raise.
				isClicked = true;
			}
		});
		sc.setOnMouseReleased(event -> {
			isClicked = false;
		});

// ----------------Animation Hub------------------//
		// Instantiate the animation timer
		new AnimationTimer() {
			// This is essentially just a while loop controlled by javaFX
			@Override
			public void handle(long now) {
				if(canPlay==false) {
					stop();
				}

				if(framemode==FrameMode.FrameAtTime && precedFrame==false) {
					return;
				}else if(framemode==FrameMode.FrameAtTime && precedFrame==true) {
					precedFrame = false;
				}
				
				if(useComms) {
					handleReel(reelIn);
				}else {
					handleReel(isClicked);
				}
				
				
				if(gamemode!=GameMode.Normal) {
					mode = 1;
				}
				
				if (mode == 3) {
					// clear the screen.
					gc.clearRect(0, 0, 1280, 720);
					// Image that says "Game Over, you caught # fish". Closes after 5 seconds.
					gc.drawImage(FISHLOSE, 0, 0);
					fishImage = null;
				}else if (mode == 2) {
					// clear the screen.
					gc.clearRect(0, 0, 1280, 720);

					
					// Animate the bobber being flung.
					if (System.currentTimeMillis() >= animTime + (animPos * frameRate)) {
						animPos++;
						animPos = (int) clamp(animPos, 0, 5);
					}
					// The fish was successfully caught.
					if (animPos == 5) {
						gc.drawImage(FISHWON, 0, 0);
						gc.setTextAlign(TextAlignment.LEFT);
						gc.setTextBaseline(VPos.TOP);

						gc.setFont(new Font("Timesnew Roman", 30));
						gc.setFill(Color.WHITE);
						gc.fillText("" + fishName, namePos[0], namePos[1]);
						gc.setFill(Color.CORAL);
						gc.fillText("Difficulty " + difficulty, difPos[0], difPos[1]);
						gc.drawImage(fishImage, 837, 69);
					} else {
						gc.drawImage(castAnim[4 - animPos], 0, 0);
					}
					if (scaledFish != null && animPos < 5 && animPos >= 1) {
						gc.drawImage(scaledFish, bobberPos[animPos - 1][0], bobberPos[animPos - 1][1]);
					}
				}else if (mode == 4) {
					// clear the screen.
					gc.clearRect(0, 0, 1280, 720);

					gc.drawImage(GAMEOVER, 0, 0);
				}else if (mode == 0) {
					// clear the screen.
					gc.clearRect(0, 0, 1280, 720);

					if (System.currentTimeMillis() >= waitTime && firstNoise == true) {
						bobberDown.play(1);
						firstNoise = false;
					}
					if (System.currentTimeMillis() >= animTime + (animPos * frameRate)) {
						animPos++;
						animPos = (int) clamp(animPos, 0, 4);
					}
					gc.drawImage(castAnim[animPos], 0, 0);
					if (System.currentTimeMillis() >= maxWaitTime) {
						waitTime = (Math.random() * 2.5) + 5;
						waitTime = (waitTime * 1000) + System.currentTimeMillis();
						maxWaitTime = waitTime + MAXWAITTIMEHOLD;
						firstNoise = true;
					}
				}else if (mode == -1) {
					if (System.currentTimeMillis() >= animTime + (animPos * frameRate)) {
						animPos++;
						animPos = (int) clamp(animPos, 0, 5);
					}
					if (animPos == 5) {
						gc.drawImage(IDLE, 0, 0);
					} else {
						gc.drawImage(castAnim[4 - animPos], 0, 0);
					}
				}else if (mode == 1) {					
					gc.drawImage(MINIGAME, 0, 0);
					// Generate time since last frame.
					double deltaT = (now - lastTime) / 1000000000.0;


					// Determine the fishes movement.
					double newVel = detMove();

					// Set the new fishes movement.
					fish.setyVel(clamp(Math.abs(newVel) - DECRATE * deltaT, MINFISH, MAXFISH) * ((newVel >= 0) ? 1 : -1));

					// if the player is clicking the left mouse button the fish raises.
					if (isClicked == true) {
						CA.setyVel(clamp(CA.getyVel() + MOTOR * deltaT, MINSPEED, MAXSPEED));
					} else {
						CA.setyVel(clamp(CA.getyVel() + GRAV * deltaT, MINSPEED, MAXSPEED));
					}

					// Update the fish and the Capture area in order to display its new position.
					CA.update(deltaT);
					CA.show(gc);

					fish.update(deltaT);
					fish.show(gc);

					// determine if fish is inside the colliding area.
					if (fish.collidingWith(CA)) {
						myPoints += CAPRATEUP * deltaT;
					} else {
						myPoints -= CAPRATEDOWN * deltaT;
					}
					
					//clamp myPoints between 0 and 100
					if(myPoints > CAPTUREPOINTS) {
						myPoints = CAPTUREPOINTS;
					}else if(myPoints < 0) {
						myPoints = 0;
					}

					// The size of the bar.
					double ySize = (myPoints / CAPTUREPOINTS) * CAPHEIGHT;
					// draw the bar.
					gc.drawImage(bar, 751, 692, 64, -ySize);
					// Handle capture/loss
					if (myPoints >= CAPTUREPOINTS) {
						//Fish was captured:
						mode = 2;
						animPos = 0;
						animTime = System.currentTimeMillis();
						fishCaught++;

						myPoints = CAPTUREPOINTS / 2;
						firstNoise = true;
						actualManditoryWait = System.currentTimeMillis() + manditoryWait;
						startGame();
					} else if (myPoints <= 0 && gamemode!=GameMode.SafePractice) {
						//Fish was Lost.
						startGame();
						actualManditoryWait = System.currentTimeMillis() + manditoryWait;
						// go into lose mode method
						fishLost++;

						mode = 3;
						myPoints = CAPTUREPOINTS / 2;
						firstNoise = true;
					}
				}
				
				// This will try to make fish caught/fish lost display
				gc.setTextAlign(TextAlignment.LEFT);
				gc.setTextBaseline(VPos.TOP);
				gc.setFont(new Font("Timesnew Roman", 45));
				gc.setFill(Color.LAWNGREEN);
				gc.fillText("Caught: " + fishCaught, 10, 0);
				
				gc.setTextAlign(TextAlignment.RIGHT);
				gc.setTextBaseline(VPos.TOP);
				gc.setFill(Color.RED);
				gc.fillText("Got Away: " + fishLost, 1270, 0);
				gc.setFont(new Font("Timesnew Roman", 30));
				
				gc.setTextAlign(TextAlignment.LEFT);
				gc.setTextBaseline(VPos.BOTTOM);
				gc.setFill(Color.AQUAMARINE);
				gc.fillText("Record Fish Caught: " + recordFish, 0, 720);

				
				gc.setTextAlign(TextAlignment.RIGHT);
				gc.setTextBaseline(VPos.BOTTOM);
				gc.setFill(Color.BLACK);
				gc.setFont(new Font("Timesnew Roman", 10));
				gc.fillText("FPS " + String.format("%.2f", lastFPS), 1270, 700);
				gc.fillText("Frame " + frameCount, 1270, 720);
				
				if (isRecord) {
					gc.setFont(new Font("Timesnew Roman", 20));
					gc.setTextAlign(TextAlignment.RIGHT);
					gc.setTextBaseline(VPos.BOTTOM);
					gc.setFill(Color.YELLOW);
					gc.fillText("You have beaten the record!", 1270, 720);
				}
				
				
				Double lastDT = (now - lastTime) / 1000000000;
//				print(lastDT);
				dtInfo[dtiIndex] = lastDT; //get the dt to be in milliseconds.
				
				//dtiIndex=4, startIdx = 0;
				// dtiIndex=2, startIdx=3
				int startIdx = (dtiIndex + 1) % dtInfo.length;
				double sum = 0;
				
				for(int i = 0; i < dtInfo.length; i++) {
					sum += dtInfo[(startIdx + i) % dtInfo.length];
				}
				
				dtiIndex = (dtiIndex+1)%dtInfo.length;
				
				
				
				lastFPS = 1 / (sum/dtInfo.length);
				
				root.getChildren().setAll(can);
				frameCount++;
				lastTime = now;
				
				reelIn = false;
				frameProccessed = true;
			}
		}.start();
		//Update the frame count
		// show everything.
		stage.show();
	}

	public static void handleReel(boolean isRealing) {
		
		// Depending on the current mode (see definitions), we set values and call
		// functions Here.
		if(isRealing) {
			//If the player is idle.
			if (mode == -1) {
				// Generate the random fish.
				fishNum = (int) (Math.random() * 14);
				waitTime = (Math.random() * 5) + 2.5;
				waitTime = (waitTime * 1000) + System.currentTimeMillis();
				maxWaitTime = waitTime + MAXWAITTIMEHOLD;
				fishImage = new Image(ourFish.getIMG(fishNum), 255, 255, true, false);
				scaledFish = new Image(ourFish.getIMG(fishNum), 100, 100, true, false);
				difficulty = ourFish.getDiff(fishNum);
				fishName = ourFish.getName(fishNum);
				animPos = 0;
				mode = 0;
				animTime = System.currentTimeMillis();
			}
			
			// If the player left clicks within a time window set mode to 1.
			// If the player misses the window (is too late), and the player clicks, set
			// mode to 1.
			// If the player just won or lost, wait manditoryWait amount of seconds untill
			// they can click again.
			else if (mode == 0 && (System.currentTimeMillis() >= waitTime && System.currentTimeMillis() <= maxWaitTime)) {
				// Start the game!
				mode = 1;
	
			} else if (mode == 0 && (System.currentTimeMillis() <= waitTime)) {
				// Pulled before the fish grabbed the bobber :(
				animTime = System.currentTimeMillis();
				animPos = 0;
				fishImage = null;
				fishName = null;
				scaledFish = null;
				mode = -1;
	
				// If mode == lost fish or won fish.
			} else if ((mode == 3 || mode == 2) && (System.currentTimeMillis() >= actualManditoryWait)) {
				if (mode == 2) {
	
					animPos = 5;
	
				} else if (mode == 3) {
					animPos = 0;
				}
				animTime = System.currentTimeMillis();
				fishImage = null;
				fishName = null;
				scaledFish = null;
				mode = -1;
			} else if (mode == 4 && System.currentTimeMillis() >= actualManditoryWait + 2500) {
				System.exit(-1);
			}
		}
	}
	
	
	/*
	 * Landon Zweigle Determines the fishes next velocity using its difficulty.
	 * parameters: none returns: the fishes "new" velocity *
	 */
	public static double detMove() {
		// The current time in nanoseconds.
		double cur = System.currentTimeMillis();
		// the current fishes velocity.
		double toRet = fish.getyVel();

		// if the current time is greater than or equal to the time to change.
		if (cur >= (ttc * 1000) + lt) {
			// Set lt (lasttime) to the current time to add it to the number of seconds
			// required to get, so we can have a relative time.
			lt = cur;
			// Milliseconds to wait.
			ttc = ((Math.random()) * 10 / difficulty);

			// The rest of the method is just to make the fish movement feel balanced given
			// its difficulty. Mult changes the direction.
			int mult = -1;
			if (Math.random() <= .025) {
				mult = 1;
			}
			// Depending on the fishes current velocity, we change its velocity.
			if (toRet >= 0) {
				toRet = 200 * difficulty * ((Math.random()) - (.5)) * mult;
			} else {
				toRet = 200 * difficulty * ((Math.random()) - (.5)) * mult * -1;
			}
		}
		// Return new velocity.
		return toRet;
	}

	// Landon Zweigle
	// Simple print method.
	// parameters: toPrint = object to be printed
	// returns: None.
	public static void print(Object toPrint) {
		System.out.println(toPrint.toString());
	}

	/*
	 * Landon Zweigle Clamps a value to a range parameters: val = value to be
	 * clamped, min = lower limit, max = upper limit. returns: returnedVal = the
	 * clamped value.
	 */
	public static double clamp(double val, double min, double max) {
		double returnedVal = val;
		if (val >= max) {
			returnedVal = max;
		} else if (val <= min) {
			returnedVal = min;
		}
		return returnedVal;
	}

}
// Problems: None