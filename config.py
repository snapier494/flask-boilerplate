# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/dbflask')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
