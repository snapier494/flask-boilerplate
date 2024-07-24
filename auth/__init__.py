# auth/__init__.py
from .login import login_bp
from .register import register_bp
from .logout import logout_bp
from .signup import signup_bp

def route_auth(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(signup_bp)
