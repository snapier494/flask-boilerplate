# auth/register.py
from flask import Blueprint, request, render_template, jsonify
import bcrypt
from flask_login import login_user
from feature.db import get_db_connection
from models import User 
from checkout_session import create_checkout_session  # Adjust import as necessary

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            email = request.form.get('email')
            print('username = ', username)
            print('password = ', password)
            print('email = ', email)
            conn = get_db_connection()
            print('conn = ', conn);
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            conn.commit()
            
            # Retrieve the id of the user based on their email
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cur.fetchone()[0]

            # Automatically log in the user
            user = User(user_id, username, password, email)  # Replace with your User model
            login_user(user)

            return create_checkout_session()
        
        except Exception as e:
            conn.rollback()
            return jsonify({'error': 'An error occurred during registration' + e}), 500
    return render_template('register.html')
