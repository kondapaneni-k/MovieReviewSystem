import pyodbc
import random
from datetime import datetime

# SQL Server Configuration
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=cdm-server1.database.windows.net;"
    "DATABASE=cdm-db1;"
    "UID=cdm;"
    "PWD=Keerthi@111;"
)

# Predefined list of 20 random reviews
random_reviews = [
    "This movie was absolutely thrilling, with great twists and turns. I loved the performances by the cast!",
    "A fantastic movie, filled with emotion and beautiful cinematography. Highly recommended for drama lovers.",
    "It was an okay movie. Some parts were slow, but the action sequences were fantastic. Worth a watch.",
    "A very intense and gripping film from start to finish. The storyline kept me on the edge of my seat.",
    "This was an emotional rollercoaster. The characters were well-developed, and the plot was engaging throughout.",
    "Not the best movie, but still entertaining. The effects were impressive, though the plot was predictable.",
    "A visually stunning movie with amazing special effects. The story was a bit weak, but the visuals made up for it.",
    "An underrated gem! The acting was superb, and the plot was refreshing. Definitely a must-see.",
    "I didn’t expect to like this movie, but it surprised me. The plot was fun, and the pacing was spot-on.",
    "A complete disappointment. The plot was weak, and the characters didn’t seem to have any depth.",
    "One of the best movies I’ve seen this year. The director did an incredible job, and the cast was perfect.",
    "The movie had its moments, but overall, it didn’t live up to the hype. I expected more.",
    "A solid movie, though it wasn’t groundbreaking. Still worth a watch for fans of the genre.",
    "The ending was unexpected, and I loved the character development. Definitely a movie worth rewatching.",
    "While the movie was good, it was a bit too long. Could have used some tighter editing.",
    "A thrilling ride from beginning to end. The suspense kept me hooked the entire time.",
    "Not my type of film, but I can see how others would enjoy it. The acting was decent.",
    "The plot was a little predictable, but the performances made up for it. Entertaining overall.",
    "A fun movie for the whole family. Heartwarming, with just the right amount of humor and adventure.",
    "This movie made me cry. The storytelling was heartwarming and the performances were top-notch."
]

# Function to insert a random review into the Reviews table
def insert_random_review(cursor, review_text):
    user_id = random.randint(1, 100)  # Random UserID between 1 and 100
    movie_id = random.randint(629, 1935)  # Random MovieID between 629 and 1935

    # Check if the combination of UserID and MovieID already exists
    cursor.execute("""
        SELECT COUNT(*)
        FROM Reviews
        WHERE UserID = ? AND MovieID = ?
    """, (user_id, movie_id))
    exists = cursor.fetchone()[0]

    if exists == 0:  # If no such combination exists, insert the review
        rating = random.randint(1, 10)  # Random rating between 1 and 10
        cursor.execute("""
            INSERT INTO Reviews (UserID, MovieID, Rating, ReviewText, CreatedAt)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, movie_id, rating, review_text, datetime.now()))
        return True
    else:
        return False  # Skip the insertion if the combination exists

# Main function to insert 20 random reviews
def insert_random_reviews():
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()

    # Insert 20 random reviews from the predefined list
    for review_text in random_reviews:
        success = insert_random_review(cursor, review_text)
        if success:
            conn.commit()  # Commit only if a new review was inserted

    cursor.close()
    conn.close()

# Run the script
insert_random_reviews()
