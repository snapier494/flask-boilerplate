from flask_sqlalchemy import SQLAlchemy
import uuid
from feature.db import get_db_connection

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(8), default='inactive', nullable=False)  # 'inactive' or 'active'

    def __repr__(self):
        return f'<User {self.username}>'

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        status VARCHAR(10) DEFAULT 'inactive' CHECK (status IN ('inactive', 'active'))
    );
    """
    
    try:
        cursor.execute(create_table_query)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()
