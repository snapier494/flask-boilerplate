# auth/login.py
from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_login import login_user
import bcrypt
from db.connectDB import get_db_connection  # Adjust import as necessary
from models import User  # Adjust import as necessary

forget_password_bp = Blueprint('forget_password', __name__)

@forget_password_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        print('user = ', user);
        if user:
            return jsonify({'user': user}), 200;
        else:
            error_message = "Email does not exist"  # Set the error message
            return render_template('pages/forget-password.html', error_message=error_message)
    return render_template('pages/forget-password.html')
