package APJ.Fisher;

//Parker Segelhorst
//For the fish game
//Class contains all all the information for the fish.

public class Fish{

	private String[ ] name;
	private int[ ] dif;
	private String[ ] imgs;

	public Fish(){
		this.name = new String[ ] { "King Chrimson", "Dangledook Trout", "Skew Fish", "Catpiscis",
				"Triplicata Triangle Bass", "Kungona Fish", "Magacaa", "Padon Fish", "Artyom Trout", "Mutant Carp",
				"Schmetterling Fish", "Verstehen Verwirrt Ryba", "VideoSpieler", "Oncreatieve Minnow" };
		this.dif = new int[ ] { 10, 8, 6, 1, 5, 7, 3, 4, 6, 7, 2, 9, 4, 6};
		this.imgs = new String[ ] { "fish_king-chrimson.png","fish_dangledook-trout.png","fish_skew-fish.png","fish_catpiscis.png","fish_triplicata-trianlge-bass.png","fish_kugona-fish.png","fish_magacaa.png","fish_padon-fish.png","fish_artyom-trout.png","fish_mutant-carp.png","fish_schmetterling-fish.png","fish_verstehen-verwirrt-rybe-squid.png","fish_videospieler.png","fish_oncreatieve-minnow.png"};
	}
	
	public String getName( int index )
	{
		return name[index];
	}

	public int getDiff( int index )
	{
		boolean override = true;
		int _ret;
		if(override) {
			_ret = 5;
		}else {
			_ret = dif[index];
		}
		return _ret;
	}

	public String getIMG( int index )
	{
		return ClassLoader.getSystemClassLoader().getResource(imgs[index]).toString();
	}

}
//Problems: none.