package leipflix;


public class Movie{
    private String title;

    public Movie(String title){
    	this.title = title;
    }

    public void playWithAds(){
    	System.out.println("Playing " + this.title);
		for(int i = 1; i < 4; i++){
		    System.out.println("[...]");
		    System.out.println("Ad number " + i);
		}
		System.out.println("End of the movie");
		System.out.println("Credits of " + this.title);
    }

    public void playHD(){
		System.out.println("Playing " + this.title + " in HD!");
		for(int i = 1; i < 4; i++)
		    System.out.println("the plot goes on");
		System.out.println("End of the movie");
		System.out.println("Credits of " + this.title);
    }
    
    public String toString() {
    	return this.title;
    }
}
