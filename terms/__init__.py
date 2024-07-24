# auth/__init__.py
from .terms_condition_page import terms_condition_page_bp


def route_terms(app):
    app.register_blueprint(terms_condition_page_bp)
