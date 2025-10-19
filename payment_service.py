"""
Payment service for AIstylist using Stripe
"""
import os
import stripe
from database import get_db_connection

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(user_id, price_id="price_1234567890"):
    """Create Stripe checkout session"""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('BASE_URL', 'http://127.0.0.1:5000')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('BASE_URL', 'http://127.0.0.1:5000')}/payment/cancel",
            metadata={
                'user_id': str(user_id)
            }
        )
        return session
    except Exception as e:
        print(f"Stripe checkout error: {e}")
        return None

def create_customer_portal_session(customer_id):
    """Create Stripe customer portal session"""
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{os.getenv('BASE_URL', 'http://127.0.0.1:5000')}/dashboard"
        )
        return session
    except Exception as e:
        print(f"Customer portal error: {e}")
        return None

def handle_webhook(payload, signature):
    """Handle Stripe webhook events"""
    try:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']
            
            # Update user subscription
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions 
                SET status = 'active', 
                    stripe_customer_id = ?, 
                    stripe_subscription_id = ?,
                    current_period_end = ?
                WHERE user_id = ?
            ''', (
                session['customer'],
                session['subscription'],
                datetime.fromtimestamp(session['subscription_details']['metadata']['current_period_end']),
                user_id
            ))
            
            conn.commit()
            conn.close()
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            customer_id = subscription['customer']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions 
                SET status = ?, 
                    current_period_end = ?
                WHERE stripe_customer_id = ?
            ''', (
                subscription['status'],
                datetime.fromtimestamp(subscription['current_period_end']),
                customer_id
            ))
            
            conn.commit()
            conn.close()
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            customer_id = subscription['customer']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions 
                SET status = 'cancelled'
                WHERE stripe_customer_id = ?
            ''', (customer_id,))
            
            conn.commit()
            conn.close()
        
        return True
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return False

def get_subscription_status(user_id):
    """Get user's subscription status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM subscriptions WHERE user_id = ?
    ''', (user_id,))
    
    subscription = cursor.fetchone()
    conn.close()
    
    if not subscription:
        return {
            'status': 'trial',
            'is_trial': True,
            'can_use_features': True
        }
    
    from datetime import datetime
    now = datetime.now()
    trial_ends_at = datetime.fromisoformat(subscription['trial_ends_at']) if subscription['trial_ends_at'] else None
    
    if subscription['status'] == 'trial' and trial_ends_at and now > trial_ends_at:
        return {
            'status': 'trial',
            'is_trial': True,
            'can_use_features': False,
            'trial_ends_at': trial_ends_at
        }
    
    return {
        'status': subscription['status'],
        'is_trial': subscription['status'] == 'trial',
        'can_use_features': subscription['status'] == 'active',
        'trial_ends_at': trial_ends_at
    }
