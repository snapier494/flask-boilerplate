from .contactUs import contactUs_bp
from .aboutUs import aboutUs_bp

def route_common(app):
    app.register_blueprint(contactUs_bp)
    app.register_blueprint(aboutUs_bp)