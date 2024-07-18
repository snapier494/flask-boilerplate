from flask_sqlalchemy import SQLAlchemy
import uuid
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime

db = SQLAlchemy()

# Define the ENUM type in SQLAlchemy
user_status_enum = ENUM('inactive', 'active', name='user_status', create_type=False)

class User(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(user_status_enum, default='inactive', nullable=False)  # Use ENUM type
    created = db.Column(db.DateTime, default=datetime.utcnow)  # Added created timestamp
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated timestamp


    def __init__(self, uuid, username, email, password, status):
        self.uuid = uuid
        self.username = username
        self.email = email
        self.password = password
        self.status = status

    def __repr__(self):
        return f'<User {self.username}>'

    def is_active(self):
        return self.status == 'active'
    
    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.uuid)

