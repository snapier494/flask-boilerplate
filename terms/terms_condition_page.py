# auth/login.py
from flask import Blueprint, render_template

terms_condition_page_bp = Blueprint('terms-condition-page', __name__)

@terms_condition_page_bp.route('/terms-condition-page')
def terms_condition_page():
    return render_template('pages/terms.html')