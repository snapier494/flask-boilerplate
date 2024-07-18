# checkout_session/routes.py
from flask import Blueprint, redirect, request, render_template, jsonify, json
from flask_login import current_user, login_required
import stripe
from db.connectDB import get_db_connection
from datetime import datetime
from .features import checkout_session_completed, update_subscription

create_checkout_session_bp = Blueprint('create-checkout-session', __name__)
create_portal_bp = Blueprint('create-portal-session', __name__)
webhook_bp = Blueprint('webhook_received', __name__)
checkout_bp = Blueprint('checkout', __name__)
cancel_bp = Blueprint('cancel', __name__)
success_bp = Blueprint('success', __name__)
manage_subscription_bp = Blueprint('manage_subscription', __name__)

YOUR_DOMAIN = "http://localhost:5000"  # Replace with your actual domain


@manage_subscription_bp.route('/manage')
@login_required
def manage_subscription():
    user_email = current_user.email

    # Query the database to get the subscription_id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT subscription_id FROM users WHERE email = %s", (user_email,))
    subscription_id = cur.fetchone()[0]
    conn.close()

    # Fetch the subscription from Stripe
    subscription = stripe.Subscription.retrieve(subscription_id)

    # Get the plan details
    plan_product_id = subscription['items']['data'][0]['plan']['product']
    plan_amount = subscription['items']['data'][0]['plan']['amount']
    
    # Fetch the product from Stripe
    product = stripe.Product.retrieve(plan_product_id)

    #Get the product name
    plan_product_name = product['name']

    # Convert the timestamps to datetime objects
    start_date = datetime.fromtimestamp(subscription['current_period_start'])
    end_date = datetime.fromtimestamp(subscription['current_period_end'])

    # Check if the subscription has a cancel_at field and convert it to a datetime object if it does
    cancel_date = None
    if subscription['cancel_at']:
        cancel_date = datetime.fromtimestamp(subscription['cancel_at'])

    # Pass the subscription details to the template
    return render_template('pages/manage.html', subscription=subscription, start_date=start_date, end_date=end_date, cancel_date=cancel_date, plan_product_id=plan_product_id, plan_amount=plan_amount, plan_product_name=plan_product_name)

@create_checkout_session_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        prices = stripe.Price.list(
            lookup_keys=[request.form.get('lookup_key')],
            expand=['data.product']
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + '/cancel',
            customer_email=current_user.email,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@create_portal_bp.route('/create-portal-session', methods=['POST'])
def customer_portal():
    # Retrieve the email from the logged-in user
    user_email = current_user.email

    # Query the database to get the customer_id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT customer_id FROM users WHERE email = %s", (user_email,))
    customer_id = cur.fetchone()[0]
    conn.close()

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = YOUR_DOMAIN

    portalSession = stripe.billing_portal.Session.create(
        customer=customer_id,  # Use the customer_id from the database
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook_received():
    endpoint_secret = 'whsec_BT9RsZzqBsA92oxZ1a0iX3iauz2FBQ6B'
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    if endpoint_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        sig_header = request.headers['STRIPE_SIGNATURE']
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)         
        except stripe.error.SignatureVerificationError as e:
            print('error:', str(e));
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'An unknown error occurred'}), 500
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        event_type = payload['type']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
         # Extract the necessary data
        session = event['data']['object']
        customer_id = session['customer']
        subscription_id = session['subscription']
        email = session['customer_details']['email']
        name = session['customer_details']['name']

        # Print the variables
        print("Session: ", session)
        print("Customer ID: ", customer_id)
        print("Subscription ID: ", subscription_id)
        print("Email: ", email)
        print("Name: ", name)

        # Call the function to update the database
        checkout_session_completed(email, customer_id, subscription_id, name)
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
        #print('Event data:', event['data']['object'])
        # Extract the necessary data
        subscription = event['data']['object']
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        current_period_start = subscription['current_period_start']
        current_period_end = subscription['current_period_end']
        product = subscription['plan']['product']
        status = subscription['status']

        # Print the variables
        print("Customer ID: ", customer_id)
        print("Subscription ID: ", subscription_id)
        print("Current Period Start: ", current_period_start)
        print("Current Period End: ", current_period_end)
        print("Product: ", product)
        print("Status: ", status)

        # Call the function to update the database
        update_subscription(customer_id, subscription_id, current_period_start, current_period_end, product, status)

    elif event_type == 'invoice.paid':
        print('invoice paid %s', event.id)
        #print('Event data:', event['data']['object'])
    elif event_type == 'customer.subscription.deleted':
        # Extract the subscription data
        subscription = event['data']['object']
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        current_period_start = subscription['current_period_start']
        current_period_end = subscription['current_period_end']
        product = subscription['plan']['product']
        status = subscription['status']

        print("Customer ID: ", customer_id)
        print("Subscription ID: ", subscription_id)
        print("Current Period Start: ", current_period_start)
        print("Current Period End: ", current_period_end)
        print("Product: ", product)
        print("Status: ", status)

        # Call the function to update the database
        update_subscription(customer_id, subscription_id, current_period_start, current_period_end, product, status)
        print('Subscription canceled: %s', event.id)

    return jsonify({'status': 'success'}), 200

@checkout_bp.route('/checkout')
def checkout():
    print('current_user email = ', current_user.email);
    #this changes to the landing page
    return render_template('pages/checkout.html')

@cancel_bp.route('/cancel')
def cancel():
    return render_template('pages/cancel.html')

@success_bp.route('/success')
#this changes to onboarding page
def success():
    return render_template('pages/success.html')
