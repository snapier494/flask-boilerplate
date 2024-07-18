from flask_login import current_user
from datetime import datetime
import stripe
from db.connectDB import get_db_connection

def checkout_session_completed(email, customer_id, subscription_id, name):
    # Retrieve the subscription
    subscription = stripe.Subscription.retrieve(subscription_id)
    print('subscriptions = ', subscription)
    # Extract the product, start_date, and end_date
    price_id = subscription['items']['data'][0]['plan']['id']
    product = subscription['plan']['product']
    start_date = datetime.fromtimestamp(subscription['current_period_start'])
    end_date = datetime.fromtimestamp(subscription['current_period_end'])
    
    # Get a connection to the database
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    
    if user:
        user_id = user[0]
        
        # Check if the user already has a subscription
        cur.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
        subscription = cur.fetchone()
        if not subscription:
            cur.execute("INSERT INTO subscriptions (user_id, email, customer_id, subscription_id, price_id, start_date, end_date, product, name, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (user_id, email, customer_id, subscription_id, price_id, start_date, end_date, product, name, 'active'))
        else:
            # Update users table
            cur.execute(
                """
                UPDATE subscriptions
                SET customer_id = %s, subscription_id = %s, price_id = %s, start_date = %s, end_date = %s, product = %s, status = 'active', name = %s
                WHERE email = %s
                """,
                (customer_id, subscription_id, price_id, start_date, end_date, product, name, email)
            )

        # Commit changes and close connection
        conn.commit()
        cur.close()
        conn.close()
    else:
        print(f"No user found with email: {email}")

def update_subscription(customer_id, subscription_id, current_period_start, current_period_end, product, status):
    # Convert Unix timestamps to datetime objects
    start_date = datetime.fromtimestamp(current_period_start)
    end_date = datetime.fromtimestamp(current_period_end)
    # Get a connection to the database
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM subscriptions WHERE customer_id = %s AND subscription_id = %s", (customer_id, subscription_id, ))
    subscription = cur.fetchone();
    if subscription:
        # Update subscriptions table
        cur.execute(
            """
            UPDATE subscriptions
            SET start_date = %s, end_date = %s, product = %s, status = %s
            WHERE customer_id = %s AND subscription_id = %s
            """,
            (start_date, end_date, product, status, customer_id, subscription_id)
        )
        
        # Commit changes and close connection
        conn.commit()
        cur.close()
        conn.close()
