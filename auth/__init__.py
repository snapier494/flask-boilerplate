# auth/__init__.py
from .login import login_bp
from .register import register_bp
from .logout import logout_bp
from .signup import signup_bp
from .forget_password import forget_password_bp
from .reset_password_verify_token import reset_password_verify_token_bp
from .reset_password import reset_password_bp

def route_auth(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(forget_password_bp)
    app.register_blueprint(reset_password_verify_token_bp)
    app.register_blueprint(reset_password_bp)
