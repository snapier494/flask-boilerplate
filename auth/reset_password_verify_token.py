# auth/login.py
from flask import Flask, Blueprint, request, render_template, jsonify, redirect, url_for
import os
from db.connectDB import get_db_connection  # Adjust import as necessary
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import jwt
import datetime

api_key = os.environ.get('SENDGRID_API_KEY')

reset_password_verify_token_bp = Blueprint('reset_password_verify_token', __name__)

YOUR_DOMAIN = os.getenv('YOUR_DOMAIN')  # Replace with your actual domain

JWT_EXPIRES_IN = 3600  

@reset_password_verify_token_bp.route('/reset-password/verify/<token>', methods=['GET', 'POST'])
def reset_password_verify(token):
    try:
        decoded_token = jwt.decode(token, 'secret', algorithms=['HS256'])
        print(decoded_token)
        current_time = datetime.datetime.now().timestamp()
        expiration_time = decoded_token['exp']
        if current_time > expiration_time:
            return redirect(url_for('forget_password.forget_password'))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (decoded_token['email'], ))
        user = cur.fetchone();
        if user:
            # return jsonify({'user': user}), 200
            
            return render_template('pages/reset-password.html', token = token)
        return redirect(url_for('forget_password.forget_password'))
    except Exception as e:
        # Handle any other unexpected errors
        return redirect(url_for('forget_password.forget_password'))