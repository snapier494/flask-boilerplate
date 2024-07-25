from flask import Blueprint, session, request, render_template
from flask_login import current_user
from .routes import create_checkout_session

sign_up_bp = Blueprint('sign-up', __name__)
@sign_up_bp.route('/sign-up', methods=['POST'])
def sign_up():
    lookup_key = request.form.get('lookup_key')
    if lookup_key:
        session['lookup_key'] = lookup_key
    if current_user.is_authenticated:
        return create_checkout_session()
    else:
        return render_template('pages/sign-up.html')