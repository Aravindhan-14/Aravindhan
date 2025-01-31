from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Function to initialize SQLite database (if not already created)
def init_db():
    with sqlite3.connect('contacts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_form (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                message TEXT
            )
        ''')
        conn.commit()

# Route to display the contact form
@app.route('/')
def index():
    return render_template('contact.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    # Save the form data into SQLite database
    with sqlite3.connect('contacts.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contact_form (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()

    # Redirect to a success page after form submission
    return redirect(url_for('success'))

# Route for the success page after form submission
@app.route('/success')
def success():
    return render_template('success.html')

# Main entry point of the app
if __name__ == '__main__':
    init_db()  # Initialize the database if it doesn't exist
    app.run(debug=True)
