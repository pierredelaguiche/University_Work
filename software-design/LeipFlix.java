package leipflix;


public class LeipFlix {

	public static void main(String[] args) {
		
		// Creating a relation with the class use for payments
		PaymentInterface payment = new PaymentSystem();
		
		// Creating database
		Database db = setUpSystem(payment);
		
		Login login = new Login(db, payment);
		
		// Starting the interactive part of the application
		login.start();	
	}
	
	/*
	 * Setting the system up by creating 2 admin users, 10 normal users (5 free and 5 premium), and 25 movies
	 * 
	 */
	private static Database setUpSystem(PaymentInterface payment) {
		Database db = new Database();
		
		//Creates two admins, admin0 and admin1 where the password is their username
		for(int i = 0 ; i < 2; i++) {
			User u = new User("admin" + i, "admin" + i, UserType.ADMIN);
			db.addUser(u);
			u.setDatabase(db);
			u.setPayment(payment);
		}
		
		//Creates 10 users, user0... user9
		//user passwords are identical to their usernames
		//users from 0 to 4 are free users
		//users from 5 to 9 are premium users
		for(int i = 0 ; i < 10; i++) {
			if (i < 5) {
				User u = new User("user" + i, "user" + i, UserType.FREE);
				db.addUser(u);
				u.setDatabase(db);
				u.setPayment(payment);
			} else {
				User u = new User("user" + i, "user" + i, UserType.PREMIUM);
				db.addUser(u);
				u.setDatabase(db);
				u.setPayment(payment);
			}
		}
		
		//creation of 25 movies with titles movie0...movie24
		for(int i = 0 ; i < 25; i++) {
			String title = "movie" + i;
			db.addMovie(new Movie(title));
		}
		
		return db;
	}
}
