# index/__init__.py
from .index import index_bp

def route_index(app):
    app.register_blueprint(index_bp)
