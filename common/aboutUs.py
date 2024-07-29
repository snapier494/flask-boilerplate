# auth/login.py
from flask import Blueprint, jsonify, request, render_template
from flask_login import current_user
from datetime import datetime
from decimal import Decimal
from db.connectDB import get_db_connection  # Adjust import as necessary

aboutUs_bp = Blueprint('aboutUs', __name__)

@aboutUs_bp.route('/aboutUs', methods=['GET'])
def contac_us():
    return render_template('pages/aboutUs.html')