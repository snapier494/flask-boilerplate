# auth/login.py
from flask import Flask, Blueprint, request, render_template, jsonify
import os
from db.connectDB import get_db_connection  # Adjust import as necessary
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import jwt
import datetime

api_key = os.environ.get('SENDGRID_API_KEY')

forget_password_bp = Blueprint('forget_password', __name__)

YOUR_DOMAIN = os.getenv('YOUR_DOMAIN')  # Replace with your actual domain

JWT_EXPIRES_IN = 3600  

@forget_password_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            email = user[2]
            payload = {
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRES_IN)
            }
            print('payload = ', payload);
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            message = Mail(
                from_email='andy@yourecomagent.com',
                to_emails=email,
                subject='Well Come to Flask',
                html_content=f'<p style="color: #500050;">Hello<br/><br/>We received a request to sign in using this email address {email}. If you want to sign in to your account, click this link:<br/><br/><a href="{YOUR_DOMAIN}/reset-password/verify/{token}">Reset Password </a><br/><br/>If you did not request this link, you can safely ignore this email.<br/><br/>Thanks.<br/><br/>Cheers.</p>'
            )
            sg = SendGridAPIClient(api_key)
            # response = sg.send(message)
            sg.send(message)
            success_message = "Please check email."  # Set the error message
            return render_template('pages/forget-password.html', success_message=success_message)
        else:
            error_message = "Email does not exist"  # Set the error message
            return render_template('pages/forget-password.html', error_message=error_message)
    return render_template('pages/forget-password.html')
