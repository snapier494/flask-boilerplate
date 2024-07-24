# auth/register.py
from flask import Blueprint, request, render_template, jsonify, session
import bcrypt
from flask_login import login_user
from db.connectDB import get_db_connection
from models import User 
from checkout.routes import create_checkout_session

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            email = request.form.get('email')
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone();
            
            if not user:
                cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
                conn.commit()
            else:
                error_message = "This email is already registered."  # Set the error message
                return render_template('pages/signup.html', error_message=error_message)

            
            # Retrieve the id of the user based on their email
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone();
            
            print('user = ', user);
            
            # Automatically log in the user
            user = User(uuid=user[0], username=user[1], email=user[2], password=user[3], status=user[4])  # Replace with your User model
            login_user(user)

            
            print('user = ', user);
            # return create_checkout_session()
            print('session = ', session['lookup_key']);
            return create_checkout_session()
        
        except Exception as e:
            conn.rollback()
            return render_template('pages/sign-up.html')
            # return jsonify({'error': 'An error occurred during registration' + e}), 500
    return render_template('pages/sign-up.html')
