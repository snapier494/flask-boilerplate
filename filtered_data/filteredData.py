# auth/login.py
from flask import Blueprint, jsonify, request
from flask_login import current_user
from datetime import datetime
from decimal import Decimal
from db.connectDB import get_db_connection  # Adjust import as necessary

filtered_data_bp = Blueprint('filtered_data', __name__)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@filtered_data_bp.route('/filtered-data', methods=['POST'])
def get_filtered_data():
    data = request.json

    rating = data.get('rating')
    publisher = data.get('publisher')
    min_price = data.get('min_price')
    max_price = data.get('max_price')
    author = data.get('author')
    title = data.get('title')
    min_units = data.get('min_units')
    max_units = data.get('max_units')
    min_profit_monthly = data.get('min_profit_monthly')
    max_profit_monthly = data.get('max_profit_monthly')
    limit = data.get('limit')
    offset = data.get('offset', 0)

    # Set the limit to the client's value or 200, whichever is smaller
    limit = min(limit, 200) if limit else 200

    conn = get_db_connection()
    cur = conn.cursor()

    # Build the SQL query with filters
    query = 'SELECT * FROM books WHERE 1=1'
    params = []

    if rating is not None:
        if 'min' in rating:
            query += ' AND rating >= %s'
            params.append(rating['min'])
        if 'max' in rating:
            query += ' AND rating <= %s'
            params.append(rating['max'])

    
    if publisher:
        query += ' AND publisher = %s'
        params.append('Independently published')
    
    if min_price is not None:
        query += ' AND price >= %s'
        params.append(min_price)
    
    if max_price is not None:
        query += ' AND price <= %s'
        params.append(max_price)
    
    if author:
        query += " AND author ILIKE %s"
        params.append(f'%{author}%')

    if title:
        query += " AND title ILIKE %s"
        params.append(f'%{title}%')
    
    if min_units is not None:
        query += ' AND units >= %s'
        params.append(min_units)
    
    if max_units is not None:
        query += ' AND units <= %s'
        params.append(max_units)
    
    if min_profit_monthly is not None:
        query += ' AND profit_monthly >= %s'
        params.append(min_profit_monthly)
    
    if max_profit_monthly is not None:
        query += ' AND profit_monthly <= %s'
        params.append(max_profit_monthly)

    query += ' ORDER BY RANDOM() LIMIT %s OFFSET %s'
    params.extend([limit, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()



# Convert rows to list of dictionaries
    result = [dict(zip(column_names, row)) for row in rows]
    
    # Convert Decimal objects to float
    result = [{k: decimal_default(v) if isinstance(v, Decimal) else v for k, v in row.items()} for row in result]
    print(result)
    return jsonify(result)
