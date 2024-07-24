from flask import Flask, jsonify, request, render_template, redirect, url_for, json, redirect, session
from flask_login import LoginManager, current_user
import os
import stripe
from decimal import Decimal
from dotenv import load_dotenv
from datetime import datetime
from config import Config
from models import db, User
from auth import route_auth
from checkout import route_checkout
from terms import route_terms
from db.connectDB import get_db_connection
from db.createTable import create_tables
from checkout.routes import create_checkout_session

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

# with app.app_context():
create_tables()

login_manager.login_view = 'login'

YOUR_DOMAIN = 'http://127.0.0.1:5000'

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE uuid = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4])


@app.route('/sign-up', methods=['POST'])
def sign_up():
    lookup_key = request.form.get('lookup_key')
    if lookup_key:
        session['lookup_key'] = lookup_key
    if current_user.is_authenticated:
        return create_checkout_session()
    else:
        return render_template('pages/sign-up.html')
 
# Register the authentication blueprints
route_auth(app)

# Register the checkout blueprints
route_checkout(app)

@app.route('/', methods=['GET'])
def index():
    # If user is not logged in, display landing.html template
    print('current_user authenticated = ', current_user.is_authenticated);
    if not current_user.is_authenticated:
        return render_template('pages/landing.html')

    # Retrieve the email from the logged-in user
    print('go to index.html');
    user_email = current_user.email
    user_id = current_user.uuid
    print('user_id = ', user_id);
    # Query the database to get the customer_id and end_date
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    print('result = ', result)
    if not result:
        return render_template('pages/landing.html')
    else: 
        customer_id = result[0]
        end_date = result[7]  # Assuming this is a string in the correct format

        if customer_id is None:
            return render_template('pages/landing.html')

        # If customer_id is not null and end_date is in the future, render index.html
        elif end_date > datetime.now():
            return render_template('pages/index.html')

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

route_terms(app)

if __name__ == "__main__":
    app.run(debug=True)