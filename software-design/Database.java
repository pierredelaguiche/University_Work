package leipflix;

import java.util.ArrayList;
import java.util.List;

public class Database {
	
	private List<User> users;
	private List<Movie> movies;
	
	public Database() {
		users = new ArrayList<User>();
		movies = new ArrayList<Movie>();
	}
	
	public void addUser(User user) {
		users.add(user);
	}
	
	public void addMovie(Movie movie) {
		movies.add(movie);
	}
	
	public List<Movie> getMovies() {
		return movies;
	}
	
	public List<User> getUsers() {
		return users;
	}
	
	public User findUser(String username) {
		for (User u : users)
			if (u.getUserName().equals(username))
				return u;
		return null;
	}

}
