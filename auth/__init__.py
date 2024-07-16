# auth/__init__.py
from flask import Blueprint

from .login import login_bp
from .register import register_bp
from .logout import logout_bp

def route_auth(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(logout_bp)
