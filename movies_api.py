import requests
import pyodbc
import time

# TMDb API Configuration
API_KEY = "5f77d4a4065a7f542dc5cdac68774112"  # Replace with your TMDb API key
BASE_URL = "https://api.themoviedb.org/3"

# SQL Server Configuration
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=cdm-server1.database.windows.net;"
    "DATABASE=cdm-db1;"
    "UID=cdm;"
    "PWD=Keerthi@111;"
)


# Fetch movies using TMDb API
def fetch_movies(page=1):
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&language=en-US&sort_by=popularity.desc&page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error fetching movies: {response.status_code}, {response.text}")
        return []

# Check if a movie with the given TMDbID already exists in the database
def movie_exists(cursor, tmdb_id):
    cursor.execute("SELECT COUNT(*) FROM Movies WHERE TMDbID = ?", (tmdb_id,))
    return cursor.fetchone()[0] > 0

# Insert movie data into the Movies table
def insert_movie(cursor, movie):
    try:
        tmdb_id = movie.get("id")
        if not movie_exists(cursor, tmdb_id):  # Only insert if the movie doesn't already exist
            cursor.execute("""
                INSERT INTO Movies (Title, Released, Genre, Language, Country, PosterURL, TMDbID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                movie.get("title"),
                movie.get("release_date"),
                ", ".join([genre["name"] for genre in movie.get("genres", [])]),
                movie.get("original_language"),
                movie.get("production_countries", [{}])[0].get("name", ""),
                f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
                tmdb_id
            ))
            return True
        else:
            print(f"Movie with TMDbID {tmdb_id} already exists. Skipping insertion.")
            return False
    except Exception as e:
        print(f"Error inserting movie: {e}")
        return False

# Main function to fetch and insert movies
def populate_movies():
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()

    movie_count = 0
    for page in range(96, 100):  # Fetch 10 pages of movies (100 movies in total)
        movies = fetch_movies(page)
        if not movies:
            break

        for movie in movies:
            print(f"Processing movie: {movie['title']}")
            if insert_movie(cursor, movie):
                movie_count += 1
                conn.commit()

            if movie_count >= 1000:  # Stop after inserting 1000 movies
                print("Inserted 1000 movies. Stopping.")
                break

        if movie_count >= 1000:
            break

        time.sleep(1)  # Avoid API rate limits

    cursor.close()
    conn.close()

# Run the script
populate_movies()
