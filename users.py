import pyodbc
import random
import string
from datetime import datetime, timedelta
import hashlib

# SQL Server Configuration
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=cdm-server1.database.windows.net;"
    "DATABASE=cdm-db1;"
    "UID=cdm;"
    "PWD=Keerthi@111;"
)

# Function to generate a random string of letters and digits
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to generate a random email
def generate_random_email():
    return generate_random_string(10) + "@gmail.com"

# Function to generate a hashed password
def generate_hashed_password(password="password123"):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to generate a random datetime within the last 30 days
def generate_random_datetime():
    random_days = random.randint(1, 30)
    return datetime.now() - timedelta(days=random_days)

# Function to insert a random user into the Users table
def insert_random_user(cursor):
    username = generate_random_string(10)
    email = generate_random_email()
    password_hash = generate_hashed_password()
    created_at = generate_random_datetime()
    last_login = generate_random_datetime()

    cursor.execute("""
        INSERT INTO Users (Username, Email, PasswordHash, CreatedAt, LastLogin)
        VALUES (?, ?, ?, ?, ?)
    """, (username, email, password_hash, created_at, last_login))

# Main function to insert multiple random users
def insert_random_users():
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()

    # Insert 100 random users into the Users table
    for _ in range(100):  # Adjust this number for more or fewer users
        insert_random_user(cursor)
        conn.commit()  # Commit after each user insertion

    cursor.close()
    conn.close()

# Run the script
insert_random_users()
