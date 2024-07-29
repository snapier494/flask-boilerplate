# auth/login.py
from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user
import bcrypt
from db.connectDB import get_db_connection  # Adjust import as necessary
from models import User  # Adjust import as necessary

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password').encode('utf-8')
        print('email = ', email)
        print('password = ', password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
            login_user(User(user[0], user[1], user[2], user[3], user[4]))
            return redirect(url_for('index.index'))
        else:
            error_message = "Email and Password is invalid."  # Set the error message
            return render_template('pages/login.html', error_message=error_message)
    return render_template('pages/login.html')
