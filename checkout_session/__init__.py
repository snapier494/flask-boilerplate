# checkout_session/__init__.py
from .routes import checkout_bp

def create_checkout_session(app):
    app.register_blueprint(checkout_bp)