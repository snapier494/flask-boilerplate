from .filteredData import filtered_data_bp

def route_filtered_data(app):
    app.register_blueprint(filtered_data_bp)