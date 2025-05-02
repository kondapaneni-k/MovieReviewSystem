from flask import Flask, request, redirect, render_template, flash, url_for,jsonify,session
from flask_cors import CORS
from db import get_connection
import bcrypt
import random

app = Flask(__name__)
app.secret_key = "development_key_only"

CORS(app)

#login page
@app.route('/')
def home():
    return render_template('index.html')

#handling login
@app.route('/', methods=['POST'])
def handle_login():
    data = request.get_json()

    # Extract login details
    username_or_email = data.get('username')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Username/email and password are required.'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Query for user by username or email
        cursor.execute("""
            SELECT UserID, Email, PasswordHash
            FROM Users
            WHERE Username = ? OR Email = ?
        """, (username_or_email, username_or_email))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            user_id, email, password_hash = user
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                session['user_id'] = user_id  # Save UserID in session
                session['email'] = email     # Save Email in session
                return jsonify({'success': True, 'message': 'Login successful!', 'redirect': '/userpage'})
            else:
                return jsonify({'success': False, 'message': 'Invalid password.'}), 401

        return jsonify({'success': False, 'message': 'User not found.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': 'Error: ' + str(e)}), 500

#registratio page
@app.route('/register')
def register_page():
    return render_template('register.html')

#handling registrations
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    # Extract user data from the request
    first_name = data['firstName']
    last_name = data['lastName']
    gender = data['gender']
    dob = data['dob']
    email = data['email']
    password = data['password']

    # Basic validation
    if not first_name or not last_name or not gender or not dob or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required!'}), 400

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Insert user into the Users table
        cursor.execute("""
            INSERT INTO Users (Username, Email, PasswordHash, CreatedAt)
            VALUES (?, ?, ?, GETDATE())
        """, (f"{first_name} {last_name}", email, hashed_password.decode('utf-8')))

        # Commit transaction
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'User registered successfully!'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': 'Error: ' + str(e)}), 500
    
#terms and conditions page
@app.route('/terms')
def terms_page():
    return render_template('terms.html')

#about page
@app.route('/about')
def about_page():
    return render_template('about.html')

#contact page
@app.route('/contact')
def contact_page():
    return render_template('contact.html')

#helpline page
@app.route('/helpline')
def helpline_page():
    return render_template('helpline.html')

#settings page
@app.route('/settings')
def settings_page():
    return render_template('settings.html')

#upadting user details
@app.route('/update_settings', methods=['POST'])
def update_settings():
    # Get form data
    email = request.form.get('email')
    current_password = request.form.get('password')
    new_password = request.form.get('newpassword')

    try:
        # Connect to the database
        conn = get_connection()
        cursor = conn.cursor()

        # Retrieve the user record by email
        cursor.execute("SELECT PasswordHash FROM Users WHERE Email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            flash("Email not found!", "danger")
            return redirect(url_for('settings_page'))

        # Extract the stored password hash
        stored_password_hash = user[0]

        # Verify the current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            flash("Incorrect current password!", "danger")
            return redirect(url_for('settings_page'))

        # Hash the new password
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the password in the database
        cursor.execute("UPDATE Users SET PasswordHash = ? WHERE Email = ?", (hashed_new_password, email))
        conn.commit()

        flash("Password updated successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('settings_page'))

#home page after login
@app.route('/userpage')
def userpage_page():
    return render_template('userpage.html')

#load movies from movie dataset to home page
@app.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Generate 30 random movie IDs between 629 and 1935
        random_movie_ids = random.sample(range(629, 1936), 100)

        # Convert the list of random IDs into a comma-separated string for the SQL query
        random_movie_ids_str = ', '.join(map(str, random_movie_ids))

        # Fetch movies with the randomly selected IDs, including the MovieID
        cursor.execute(f"""
            SELECT MovieID, Title, Released, PosterURL
            FROM Movies
            WHERE MovieID IN ({random_movie_ids_str})
            ORDER BY Released ASC
        """)
        
        movies = cursor.fetchall()

        movie_list = []
        for movie in movies:
            movie_list.append({
                'MovieID': movie[0],  # Append MovieID to the movie data
                'Title': movie[1],
                'Released': movie[2],
                'PosterURL': movie[3] if movie[3] else None
            })

        cursor.close()
        conn.close()

        return jsonify(movie_list), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

#individual movie review page
@app.route('/moviereview')
def moviereview_page():
    movie_id = request.args.get('movie_id')  # Get the movie ID from the query string

    if not movie_id:
        return redirect(url_for('userpage_page'))  # Redirect to the home page if no movie ID is provided

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch movie details based on the movie ID
        cursor.execute("""
            SELECT Title, Released, PosterURL, Genre
            FROM Movies
            WHERE MovieID = ?
        """, (movie_id,))
        
        movie = cursor.fetchone()

        if movie:
            movie_details = {
                'Title': movie[0],
                'Released': movie[1],
                'PosterURL': movie[2] if movie[2] else '../static/images/null.jpg',
                'Genre': movie[3],
            }
        else:
            movie_details = None

        # Fetch reviews for the movie
        cursor.execute("""
            SELECT u.Username, r.ReviewText, r.CreatedAt
            FROM Reviews r
            JOIN Users u ON r.UserID = u.UserID
            WHERE r.MovieID = ?
            ORDER BY r.CreatedAt DESC
        """, (movie_id,))

        reviews = [
            {'Username': review[0], 'ReviewText': review[1], 'CreatedAt': review[2]}
            for review in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        # Pass both movie details and reviews to the template
        return render_template('movie_review.html', movie=movie_details, reviews=reviews)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', message="Error fetching movie details.")

#add review
@app.route('/api/add-review', methods=['POST'])
def add_review():
    try:
        # Retrieve the request data
        data = request.get_json()
        movie_id = data.get('movieId')
        review_text = data.get('reviewText')

        # Validate inputs
        if not movie_id or not review_text:
            return jsonify({'success': False, 'message': 'Movie ID and review text are required.'}), 400

        # Fetch the logged-in user's email from the session
        email = session.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'User not logged in.'}), 401

        conn = get_connection()
        cursor = conn.cursor()

        # Fetch the UserID using the logged-in user's email
        cursor.execute("""
            SELECT UserID FROM Users WHERE Email = ?
        """, (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        user_id = user[0]

        # Insert the review into the database
        cursor.execute("""
            INSERT INTO Reviews (UserID, MovieID, ReviewText, CreatedAt)
            VALUES (?, ?, ?, GETDATE())
        """, (user_id, movie_id, review_text))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Review added successfully!'}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

#your reviews page
@app.route('/yourreview')
def yourreview_page():
    try:
        # Check if user is logged in
        email = session.get('email')
        if not email:
            return redirect(url_for('home'))  # Redirect to login if not logged in

        conn = get_connection()
        cursor = conn.cursor()

        # Fetch the UserID of the logged-in user
        cursor.execute("""
            SELECT UserID FROM Users WHERE Email = ?
        """, (email,))
        user = cursor.fetchone()

        if not user:
            return render_template('error.html', message="User not found.")

        user_id = user[0]

        # Fetch reviews written by the user
        cursor.execute("""
            SELECT m.Title, r.ReviewText, m.PosterURL
            FROM Reviews r
            JOIN Movies m ON r.MovieID = m.MovieID
            WHERE r.UserID = ?
        """, (user_id,))

        reviews = [{'Title': review[0], 'ReviewText': review[1], 'PosterURL': review[2]} for review in cursor.fetchall()]

        cursor.close()
        conn.close()

        # Pass reviews to the template
        return render_template('your_review.html', reviews=reviews)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', message="Error fetching reviews.")

if __name__ == '__main__':
    app.run(debug=True)
