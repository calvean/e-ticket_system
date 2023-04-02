#!/usr/bin/python3
import mysql.connector
import db
import uuid
from datetime import datetime
from event import get_event

def create_order(event_id, user_id, price, num_tickets):
    order_id = str(uuid.uuid4())
    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # calculate the total cost of the order
    total_cost = price * num_tickets

    # create a new order in the database
    conn = db.create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (id, event_id, user_id, num_tickets, price, total_cost, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)', (order_id, event_id, user_id, num_tickets, price, total_cost, created_at))
    conn.commit()
    conn.close()

    return order_id


def book_ticket(event_id, user_id, price, num_tickets):
    event = get_event(event_id)
    if not event:
        return {'error': 'Event not found.'}, 404

    # create a new order with the specified number of tickets
    order_id = create_order(event_id, user_id, price, num_tickets)

    # redirect the user to the PayPal payment page with the order details
    redirect_url = create_paypal_payment(price, order_id)

    return {'redirect_url': redirect_url}

