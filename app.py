from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, json, redirect, current_app, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import psycopg2
import os
import stripe
from html import escape
from decimal import Decimal
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import datetime
from datetime import datetime
from config import Config
from models import db, User
from auth import route_auth

load_dotenv()

# This is your test secret API key.
stripe.api_key = 'sk_test_51PM9N5GrYum9FiR6AOFETCmRxCNr2YKl37NNFgXgw8FTUdBjyDxHNxlcaY8Fm4kLVBVVjRQeEGpY5A0l5p9QqvQG00mPN5hWMT'

app = Flask(__name__,
    static_url_path='',
    static_folder='static')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()  # This will create the tables if they don't exist

login_manager.login_view = 'login'

YOUR_DOMAIN = 'http://192.168.0.8:8000/'

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

with app.app_context():
    # Create tables if they don't exist
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2], user[3])


@app.route('/sign-up', methods=['POST'])
def signup():
    lookup_key = request.form.get('lookup_key')
    if lookup_key:
        session['lookup_key'] = lookup_key
        print(lookup_key)
    if current_user.is_authenticated:
        return create_checkout_session()
    else:
        return render_template('register.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         try:
#             username = request.form.get('username')
#             password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#             email = request.form.get('email')
#             print(email)

#             conn = get_db_connection()
#             cur = conn.cursor()
#             cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
#             conn.commit()
            
#             # Retrieve the id of the user based on their email
#             cur.execute("SELECT id FROM users WHERE email = %s", (email,))
#             user_id = cur.fetchone()[0]

#             # Automatically log in the user
#             user = User(user_id, username, password, email)  # Replace with your User model
#             print(user)
#             login_user(user)

#             # Redirect to the create-checkout-session route
#             return create_checkout_session()
        
#         except Exception as e:
#             # Rollback the transaction in case of error
#             conn.rollback()
#             # Log the error for debugging
#             print(str(e))
#             # Return a response with a 500 Internal Server Error status code
#             return jsonify({'error': 'An error occurred during registration'}), 500
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password').encode('utf-8')
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cur.fetchone()
#         if user and bcrypt.checkpw(password, user[2].encode('utf-8')):
#             login_user(User(user[0], user[1], user[2],user[3]))
#             return redirect(url_for('index'))
#         else:
#             return 'Invalid username or password'
#     return render_template('login.html')

# @app.route('/logout')
# @login_required
# def logout():
#     #I can change this to the index route instead
#     logout_user()
#     return redirect(url_for('index'))

# Register the authentication blueprints
# route_auth(app)

@app.route('/manage')
@login_required
def manage_subscription():
    user_email = current_user.email

    # Query the database to get the subscription_id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT subscription_id FROM users WHERE email = %s", (user_email,))
    subscription_id = cur.fetchone()[0]
    conn.close()

    # Fetch the subscription from Stripe
    subscription = stripe.Subscription.retrieve(subscription_id)

    # Get the plan details
    plan_product_id = subscription['items']['data'][0]['plan']['product']
    plan_amount = subscription['items']['data'][0]['plan']['amount']
    
    # Fetch the product from Stripe
    product = stripe.Product.retrieve(plan_product_id)

    #Get the product name
    plan_product_name = product['name']

    # Convert the timestamps to datetime objects
    start_date = datetime.fromtimestamp(subscription['current_period_start'])
    end_date = datetime.fromtimestamp(subscription['current_period_end'])

    # Check if the subscription has a cancel_at field and convert it to a datetime object if it does
    cancel_date = None
    if subscription['cancel_at']:
        cancel_date = datetime.fromtimestamp(subscription['cancel_at'])

    # Pass the subscription details to the template
    return render_template('manage.html', subscription=subscription, start_date=start_date, end_date=end_date, cancel_date=cancel_date, plan_product_id=plan_product_id, plan_amount=plan_amount, plan_product_name=plan_product_name)

@app.route('/')
def index():
    # If user is not logged in, display landing.html template
    if not current_user.is_authenticated:
        return render_template('landing.html')

    # Retrieve the email from the logged-in user
    user_email = current_user.email

    # Query the database to get the customer_id and end_date
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT customer_id, end_date FROM users WHERE email = %s", (user_email,))
    result = cur.fetchone()
    customer_id = result[0]
    end_date = result[1]

    #print(f"end_date: {end_date}")
    #print(f"datetime.now(): {datetime.now()}")
    #print(f"end_date > datetime.now(): {end_date > datetime.now()}")
    # If customer_id is null, redirect to create-checkout-session route
    if customer_id is None:
        return render_template('landing.html')

    # If customer_id is not null and end_date is in the future, render index.html
    elif end_date > datetime.now():
        return render_template('index.html')

    # If customer_id is not null and end_date is in the past, redirect to manage subscription
    else:
        return redirect(url_for('manage_subscription'))

@app.route('/filtered-data', methods=['POST'])
def get_filtered_data():
    data = request.json

    rating = data.get('rating')
    publisher = data.get('publisher')
    min_price = data.get('min_price')
    max_price = data.get('max_price')
    author = data.get('author')
    title = data.get('title')
    min_units = data.get('min_units')
    max_units = data.get('max_units')
    min_profit_monthly = data.get('min_profit_monthly')
    max_profit_monthly = data.get('max_profit_monthly')
    limit = data.get('limit')
    offset = data.get('offset', 0)

    # Set the limit to the client's value or 200, whichever is smaller
    limit = min(limit, 200) if limit else 200

    conn = get_db_connection()
    cur = conn.cursor()

    # Build the SQL query with filters
    query = 'SELECT * FROM books WHERE 1=1'
    params = []

    if rating is not None:
        if 'min' in rating:
            query += ' AND rating >= %s'
            params.append(rating['min'])
        if 'max' in rating:
            query += ' AND rating <= %s'
            params.append(rating['max'])

    
    if publisher:
        query += ' AND publisher = %s'
        params.append('Independently published')
    
    if min_price is not None:
        query += ' AND price >= %s'
        params.append(min_price)
    
    if max_price is not None:
        query += ' AND price <= %s'
        params.append(max_price)
    
    if author:
        query += " AND author ILIKE %s"
        params.append(f'%{author}%')

    if title:
        query += " AND title ILIKE %s"
        params.append(f'%{title}%')
    
    if min_units is not None:
        query += ' AND units >= %s'
        params.append(min_units)
    
    if max_units is not None:
        query += ' AND units <= %s'
        params.append(max_units)
    
    if min_profit_monthly is not None:
        query += ' AND profit_monthly >= %s'
        params.append(min_profit_monthly)
    
    if max_profit_monthly is not None:
        query += ' AND profit_monthly <= %s'
        params.append(max_profit_monthly)

    query += ' ORDER BY RANDOM() LIMIT %s OFFSET %s'
    params.extend([limit, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()



# Convert rows to list of dictionaries
    result = [dict(zip(column_names, row)) for row in rows]
    
    # Convert Decimal objects to float
    result = [{k: decimal_default(v) if isinstance(v, Decimal) else v for k, v in row.items()} for row in result]
    print(result)
    return jsonify(result)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        prices = stripe.Price.list(
            lookup_keys=[session.get('lookup_key')],
            expand=['data.product']
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN +
            '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + '/cancel',
            customer_email=current_user.email,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@app.route('/create-portal-session', methods=['POST'])
def customer_portal():
    # Retrieve the email from the logged-in user
    user_email = current_user.email

    # Query the database to get the customer_id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT customer_id FROM users WHERE email = %s", (user_email,))
    customer_id = cur.fetchone()[0]
    conn.close()

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = YOUR_DOMAIN

    portalSession = stripe.billing_portal.Session.create(
        customer=customer_id,  # Use the customer_id from the database
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)

@app.route('/webhook', methods=['POST'])
def webhook_received():
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    webhook_secret = 'whsec_59d77d284d66625ef2354ce9a4901e8610ea99b4ed3f5c204b03b7ddcba7267f'
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
         # Extract the necessary data
        session = event['data']['object']
        customer_id = session['customer']
        subscription_id = session['subscription']
        email = session['customer_details']['email']
        name = session['customer_details']['name']

        # Print the variables
        print("Session: ", session)
        print("Customer ID: ", customer_id)
        print("Subscription ID: ", subscription_id)
        print("Email: ", email)
        print("Name: ", name)

        # Call the function to update the database
        checkout_session_completed(email, customer_id, subscription_id, name)
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
        #print('Event data:', event['data']['object'])
        # Extract the necessary data
        subscription = event['data']['object']
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        current_period_start = subscription['current_period_start']
        current_period_end = subscription['current_period_end']
        product = subscription['plan']['product']
        status = subscription['status']

        # Print the variables
        print("Customer ID: ", customer_id)
        print("Subscription ID: ", subscription_id)
        print("Current Period Start: ", current_period_start)
        print("Current Period End: ", current_period_end)
        print("Product: ", product)
        print("Status: ", status)

        # Call the function to update the database
        update_subscription(customer_id, subscription_id, current_period_start, current_period_end, product, status)

    elif event_type == 'invoice.paid':
        print('invoice paid %s', event.id)
        #print('Event data:', event['data']['object'])
    elif event_type == 'customer.subscription.deleted':
        # Extract the subscription data
        subscription = event['data']['object']
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        current_period_start = subscription['current_period_start']
        current_period_end = subscription['current_period_end']
        product = subscription['plan']['product']
        status = subscription['status']

        print("Customer ID: ", customer_id)
        print("Subscription ID: ", subscription_id)
        print("Current Period Start: ", current_period_start)
        print("Current Period End: ", current_period_end)
        print("Product: ", product)
        print("Status: ", status)

        # Call the function to update the database
        update_subscription(customer_id, subscription_id, current_period_start, current_period_end, product, status)
        print('Subscription canceled: %s', event.id)

    return jsonify({'status': 'success'})

def checkout_session_completed(email, customer_id, subscription_id, name):
    # Retrieve the subscription
    subscription = stripe.Subscription.retrieve(subscription_id)

    # Extract the product, start_date, and end_date
    product = subscription['plan']['product']
    start_date = datetime.fromtimestamp(subscription['current_period_start'])
    end_date = datetime.fromtimestamp(subscription['current_period_end'])
    
    # Get a connection to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Update users table
    cur.execute(
        """
        UPDATE users
        SET customer_id = %s, subscription_id = %s, start_date = %s, end_date = %s, product = %s, status = 'active', name = %s
        WHERE email = %s
        """,
        (customer_id, subscription_id, start_date, end_date, product, name, email)
    )

    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()

def update_subscription(customer_id, subscription_id, current_period_start, current_period_end, product, status):
    # Convert Unix timestamps to datetime objects
    start_date = datetime.fromtimestamp(current_period_start)
    end_date = datetime.fromtimestamp(current_period_end)
    # Get a connection to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Update subscriptions table
    cur.execute(
        """
        UPDATE users
        SET start_date = %s, end_date = %s, product = %s, status = %s
        WHERE customer_id = %s AND subscription_id = %s
        """,
        (start_date, end_date, product, status, customer_id, subscription_id)
    )

    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()

@app.route('/checkout')
def checkout():
    #this changes to the landing page
    return render_template('checkout.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/success')
#this changes to onboarding page
def success():
    return render_template('success.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
