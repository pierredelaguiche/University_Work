package leipflix;

import java.util.Scanner;

public class Login {
	
	private Database db;
	private Scanner scanner;
	private PaymentInterface payment;
	
	public Login(Database db, PaymentInterface payment) {
		this.db = db;
		this.payment = payment;
		this.scanner = new Scanner(System.in);
	}
	
	// login/registration screen
	public void start() {
		System.out.println("Welcome to LeipFlix!");
		System.out.println("Choose an option by typing the number next to it:");
		System.out.println("1 - Login");
		System.out.println("2 - Register");
		
		int selection = getSelection(1,2);
		
		if (selection == 1)
			loginScreen();
		else
			registerScreen();
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
	
	
	// screen used when the login option is selected
	private void loginScreen() {
		User user = null;
		String userName = "";
		String password = "";
		
		do {
			System.out.println("Please type your username:");
			userName = scanner.next();	
			
			System.out.println("Please type your password:");
			password = scanner.next();
			
			user = db.findUser(userName);
			
			if(user == null || !user.getPassword().equals(password))
				System.out.println("Wrong username or password");
			
		} while(user == null || !user.getPassword().equals(password));
		
		// starting the core application after successful login
		user.mainScreen();
	}
	
	
	// screen used when the register option is selected
	private void registerScreen() {
		System.out.println("Please type your username:");
		String userName = scanner.next();	
		
		System.out.println("Please type your password:");
		String password = scanner.next();
		
		User user = new User(userName, password, UserType.FREE);
		user.setDatabase(db);
		user.setPayment(payment);
		db.addUser(user);
		
		// starting the core application after successful registration
		user.mainScreen();
	}	
}
