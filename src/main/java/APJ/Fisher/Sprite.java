package APJ.Fisher;

import javafx.scene.canvas.GraphicsContext;
import javafx.scene.image.Image;

public class Sprite
{	
		//X position.
	private double x;
		//Y position;
	private double y;

		//Y Velocity
	private double yVel;
	
		//the sprites image.
	private Image img;
	
		// the width of the hit box 
	private double width;
		//the height of the hit box;
	private double height;
	
		//The max height the sprite can achieve (more like the max height the top part of the sprite can achieve...)
	private double maxH;
	//The max height the sprite can achieve (more like the max height the top part of the sprite can achieve...)
	private double minH;
	
	private double BOUNCE_MULT = .45;
	
	public Sprite()
	{		
		this.x = 0;
		this.y = 0;
		this.maxH = 0;
		this.minH = 0;
		this.yVel = 0;
		this.height = 0;
		this.width = 0;
		this.img = null;
	}

		//Landon Zweigle
		//Change the x and y position by its velocity over time.
		//parameters: time = time that velocity was in affect (delta time).
		//returns: none.
	public void update(double time) {
		this.y -= (this.yVel * time);
		//upper
		if(this.y <=  minH ) {
			this.y = minH;
			this.yVel = -(this.yVel) * BOUNCE_MULT;
		}
		//lower
		if(this.y >=  maxH - this.height ) {
			this.y = maxH - this.height;
			this.yVel = -(this.yVel) * BOUNCE_MULT;
		}
	}
	
		//Landon Zweigle
		//Draw the image to the screen.
		// parameters: gc = the scenes current graphics context.
		// returns: none.
	public void show(GraphicsContext gc) {
		//gc.clearRect ( preX,preY,img.getWidth ( ),img.getHeight ( ) );
		gc.drawImage ( img, this.x, this.y);
	}
	
		//Landon Zweigle
		//Sets position
		//parameters: toX = x position. toY = y position.
		//returns: none.
	public void setPos(double toX, double toY) {
		this.x = toX;
		this.y = toY;
	}
	
	//Landon Zweigle
	/* Determines if this sprite is intersecting with another.
	 * parameters: toSee = the sprite we are checking.
	 * returns: returnedBool = whether or not we are intersecting with toSee.
	 */
	public boolean collidingWith(Sprite toSee) {
		boolean returnedBool = false;
		
			//the top part of "us" (one the screen).
		double meBot = this.y;
		//the bottom part of "us" (one the screen).
		double meTop = this.y + this.height;
		
		//the top part of "them" (one the screen).
		double themBot = toSee.getY ( );
		//the bottom part of "them" (one the screen).
		double themTop = toSee.getY ( ) + toSee.getHeight ( );
		
		if(((themTop <= meTop && themTop >= meBot)||(themBot >= meBot && themBot<= meTop)) || ((meBot <= themTop && meBot >= themBot) || (meTop <= themTop && meTop >= themBot))) {
			returnedBool = true;
		}
		
		
		return returnedBool;
	}
	
	//Some of these getters and/or setters may not be required.
	
	public double getWidth( )
	{
		return width;
	}
	
	public void setWidth( int d )
	{
		this.width = d;
	}
	
	public double getHeight( )
	{
		return height;
	}
	
	public void setHeight( int height )
	{
		this.height = height;
	}
	
	public double getX( )
	{
		return x;
	}

	public void setX( double x )
	{
		this.x = x;
	}

	public double getY( )
	{
		return y;
	}

	public void setY( double y )
	{
		this.y = y;
	}

	public double getyVel( )
	{
		return yVel;
	}

	public void setyVel( double yVel )
	{
		this.yVel = yVel;
	}

	public Image getImg( )
	{
		return img;
	}

	public void setImg( Image img )
	{
		this.img = img;
	}
	public double getMaxH( )
	{
		return maxH;
	}

	public void setMaxH( double maxH )
	{
		this.maxH = maxH;
	}

	public double getMinH( )
	{
		return minH;
	}

	public void setMinH( double minH )
	{
		this.minH = minH;
	}
}
//problems: none.
