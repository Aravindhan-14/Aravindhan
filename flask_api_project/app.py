from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from twilio.rest import Client
import stripe

app = Flask(__name__)

# Stripe API setup (use your actual Stripe secret key)
stripe.api_key = 'your_stripe_secret_key'

# Twilio API setup (use your actual Twilio SID and Auth Token)
twilio_sid = 'your_twilio_sid'
twilio_auth_token = 'your_twilio_auth_token'
twilio_client = Client(twilio_sid, twilio_auth_token)

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# Route to display the form and save data to the database
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        
        # Insert user into the database
        conn = sqlite3.connect('app.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
        conn.commit()
        conn.close()

        # Send SMS and WhatsApp messages
        send_sms(phone)
        send_whatsapp(phone)

        return redirect(url_for('index'))
    
    return render_template('index.html')

# Function to send an SMS via Twilio
def send_sms(phone):
    message = twilio_client.messages.create(
        body="Thank you for signing up!",
        from_='+your_twilio_phone',
        to=phone
    )

# Function to send a WhatsApp message via Twilio
def send_whatsapp(phone):
    message = twilio_client.messages.create(
        body="Thank you for signing up on our website!",
        from_='whatsapp:+your_twilio_whatsapp_number',
        to=f'whatsapp:{phone}'
    )

# Route to handle payments (using Stripe)
@app.route('/payment', methods=['POST'])
def payment():
    user_id = request.form['user_id']
    amount = request.form['amount']
    
    # Create a Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=int(float(amount) * 100),  # Stripe accepts amount in cents
        currency='usd',
        payment_method=request.form['payment_method_id'],
        confirmation_method='manual',
        confirm=True
    )

    # Record the payment in the database
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("INSERT INTO payments (user_id, amount, status) VALUES (?, ?, ?)", (user_id, amount, 'completed'))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Initialize the database and create tables
    app.run(debug=True)
