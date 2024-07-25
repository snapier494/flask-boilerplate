from flask import Flask
from flask_login import LoginManager
import os
import stripe
from dotenv import load_dotenv
from config import Config
from models import db, User
from auth import route_auth
from checkout import route_checkout
from terms import route_terms
from index import route_index
from filtered_data import route_filtered_data
from db.connectDB import get_db_connection
from db.createTable import create_tables

load_dotenv()

# This is your test secret API key.
stripe.api_key = os.getenv("STRIPE_API_KEY")

print('stripe.api_key = ', stripe.api_key)

app = Flask(__name__,
    static_url_path='',
    static_folder='static')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config.from_object(Config)

db.init_app(app)

# with app.app_context():
create_tables()

login_manager.login_view = 'login'

YOUR_DOMAIN = 'http://127.0.0.1:5000'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE uuid = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4])

 
route_auth(app)
route_checkout(app)
route_index(app)
route_filtered_data(app)
route_terms(app)

if __name__ == "__main__":
    app.run(debug=True)