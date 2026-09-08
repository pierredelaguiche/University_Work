package leipflix;

import java.util.Scanner;

public class User{
    private String userName;
    private String password;
    private int moviesPerPage;
    private UserType type;
    private Database db;
    private Scanner scanner;
    private PaymentInterface payment;

    public User(String name, String password, UserType type) {
    	this.userName = name;
    	this.password = password;
    	this.type = type;
    	this.moviesPerPage = 5;
    	this.scanner = new Scanner(System.in);
    }
    
    // required getters and setters
    public void setDatabase(Database db) {
    	this.db = db;
    }
    
    public String getPassword() {
    	return password;
    }
    
    public String getUserName() {
    	return userName;
    }
    
    private void setPassword(String newPassword) {
    	password = newPassword;
    }
    
	public void setPayment(PaymentInterface payment) {
		this.payment = payment;
	}
    
    // Methods for command line interactions
	
	// Main menu once logged in
    public void mainScreen() {
    	System.out.println("Welcome to LeipFlix, " + userName + "!");
    	
    	int selection = 0; 
    	
    	do {
    		System.out.println("Select an option among the following:");
    		System.out.println("1 - edit profile");
    		System.out.println("2 - browse and play movies");
    		System.out.println("3 - logout");
    		if(type == UserType.ADMIN)
    			System.out.println("4 - add an admin account");
    		
    		if(type == UserType.ADMIN)
    			selection = getSelection(1, 4);
    		else
    			selection = getSelection(1, 3);
    		
    		switch (selection) {
    			case 1 :
    				editScreen();
    				break;
    			case 2 :
    				browseScreen();
    				break;
    			case 4 :
    				adminScreen();
    				break;
    			default :
    				break;
    		}
    		
    	} while (selection != 3);
    	
    	System.out.println("Goodbye, " + userName + "!");
    }
    
    // editing menu
    private void editScreen() {
    	
    	int selection = 0; 
    	
    	do {
    		System.out.println("Select an option among the following:");
    		System.out.println("1 - change password");
    		System.out.println("2 - change number of movies per page");
    		System.out.println("3 - go back");
    		if(type == UserType.FREE)
    			System.out.println("4 - subscribe to premium");
    		if(type == UserType.PREMIUM)
    			System.out.println("4 - unsubscribe");
    		
    		selection = getSelection(1, 4);
    		
    		switch (selection) {
    			case 1 :
    				System.out.println("Input new password:");
    				setPassword(scanner.next());
    				System.out.println("Password changed successfully");
    				System.out.println();
    				break;
    			case 2 :
    				setMoviesPerPage();
    				break;
    			case 4 :
    				if (type == UserType.FREE)
    					subscribe();
    				else if (type == UserType.PREMIUM)
    					unsubscribe();
    				break;
    			default :
    				break;
    		}
    		
    	} while (selection != 3);
    	
    }
    
    // menu to browse and play movies
    private void browseScreen() {
    	int selection = 0; 
    	int movie;
    	
    	do {
    		System.out.println("Select an option among the following:");
    		System.out.println("1 - browse movies");
    		System.out.println("2 - play a movie");
    		System.out.println("3 - go back");
    		
    		selection = getSelection(1, 3);
    		
    		switch (selection) {
    			case 1 :
    				movie = 0;
    				for (Movie m : db.getMovies()) {
    					System.out.println(movie + " - " + m.toString());
    					movie++;
    				}
    				break;
    			case 2 :
    				System.out.println("Select the movie based on associated id when browsing");
    				movie = getSelection(0, db.getMovies().size() - 1);
    				play(db.getMovies().get(movie));
    				break;
    			default :
    				break;
    		}
    		
    	} while (selection != 3);
    }
    
    
    // menu for adding a new admin user. Only available to admin users
    private void adminScreen() {
    	System.out.println("Type the username of the new admin account:");
    	String name = scanner.next();
    	System.out.println("Type the password of the new admin account:");
    	String password = scanner.next();
    	db.addUser(new User(name, password, UserType.ADMIN));
    	System.out.println("New admin " + name + " added successfully");
    }
    
    
    // officially a setter for the moviesPerPage attribute,
    // but it's implementation is more complex since it is based on interaction with the user
	private void setMoviesPerPage() {
		int selection = 0;
		
		do {
			System.out.println("How many movies per page while browsing? Only possible options are 5, 10, or 15");
			
			if (scanner.hasNextInt())
				selection = scanner.nextInt();
			else 
				scanner.next();
			
		} while (selection != 5 && selection != 10 && selection != 15);
		
		this.moviesPerPage = selection;
		
		System.out.println("Number of movies per page set up correctly!");
		System.out.println();
	}
	
	// auxiliary method to simplify the selection process on different screens
	// it performs some basic input validation
    private int getSelection(int lowerbound, int upperbound) {
		int selection = 0;
		
		while (selection == 0) {
			if(scanner.hasNextInt())
				selection = scanner.nextInt();
			else {
				scanner.next();
				selection = 0;
			}
			
			if (selection < lowerbound || selection > upperbound) {
				System.out.println("Invalid input! Try again.");
				selection = 0;
			}
		}
		
		return selection;
    }

    
    // free users can only watch with Ads, premium and admin users in HD
    private void play(Movie movie) {
    	if (type == UserType.FREE)
    		movie.playWithAds();
    	else
    		movie.playHD();
    }

    // methods to move from free to premium and vice versa
    private void subscribe(){
    	payment.performPayment();
    	type = UserType.PREMIUM;
    }

    private void unsubscribe(){
    	type = UserType.FREE;
    }
}
