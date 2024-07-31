# auth/login.py
from flask import Flask, Blueprint, request, render_template, jsonify, redirect, url_for
import os
from db.connectDB import get_db_connection  # Adjust import as necessary
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import jwt
import datetime
import bcrypt

api_key = os.environ.get('SENDGRID_API_KEY')

reset_password_bp = Blueprint('reset_password', __name__)

YOUR_DOMAIN = os.getenv('YOUR_DOMAIN')  # Replace with your actual domain

JWT_EXPIRES_IN = 3600  

@reset_password_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = request.form
        password = data.get('password')
        confirm_password = data.get('confirm-password')
        if password != confirm_password:
            error_message = 'Passwords are not same'
            return render_template('pages/reset-password.html', token = token, error_message=error_message)
        decoded_token = jwt.decode(token, 'secret', algorithms=['HS256'])
        current_time = datetime.datetime.now().timestamp()
        expiration_time = decoded_token['exp']
        if current_time > expiration_time:
            return redirect(url_for('forget_password.forget_password'))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (decoded_token['email'], ))
        user = cur.fetchone();
        if user:            
            email = decoded_token['email']
            password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute(
                """
                UPDATE users
                SET password = %s
                WHERE email = %s
                """,
                (password, email, )
            )
            conn.commit();
            return redirect(url_for('login.login'))
        return redirect(url_for('forget_password.forget_password'))
    except Exception as e:
        # Handle any other unexpected errors
        return redirect(url_for('forget_password.forget_password'))