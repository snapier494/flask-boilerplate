# checkout_session/__init__.py
from .routes import create_checkout_session_bp, create_portal_bp, webhook_bp, checkout_bp, cancel_bp, success_bp, manage_subscription_bp
from .signUp import sign_up_bp

def route_checkout(app):
    app.register_blueprint(create_checkout_session_bp)
    app.register_blueprint(create_portal_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(cancel_bp)
    app.register_blueprint(success_bp)
    app.register_blueprint(manage_subscription_bp) 
    app.register_blueprint(sign_up_bp)    