# auth/login.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime
from db.connectDB import get_db_connection  # Adjust import as necessary

index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET'])
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
