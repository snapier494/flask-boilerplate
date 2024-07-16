# auth/login.py
from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user
import bcrypt
from feature.db import get_db_connection  # Adjust import as necessary
from models import User  # Adjust import as necessary

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password').encode('utf-8')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password, user[2].encode('utf-8')):
            login_user(User(user[0], user[1], user[2], user[3]))
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')
