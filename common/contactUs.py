# auth/login.py
from flask import Blueprint, jsonify, request, render_template
from flask_login import current_user
from datetime import datetime
from decimal import Decimal
from db.connectDB import get_db_connection  # Adjust import as necessary

contactUs_bp = Blueprint('contactUs', __name__)

@contactUs_bp.route('/contactUs', methods=['GET'])
def contac_us():
    return render_template('pages/contactUs.html')