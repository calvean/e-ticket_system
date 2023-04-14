#!/usr/bin/python3

import os
import paypalrestsdk

paypal_mode = os.environ.get('PAYPAL_MODE', 'sandbox')
paypal_client_id = os.environ['PAYPAL_CLIENT_ID']
paypal_client_secret = os.environ['PAYPAL_CLIENT_SECRET']

paypalrestsdk.configure({
  "mode": paypal_mode, # or "live"
  "client_id": paypal_client_id,
  "client_secret": paypal_client_secret
})

def create_payment(amount, redirect_urls):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": redirect_urls,
        "transactions": [{
            "amount": {
                "total": amount,
                "currency": "USD"
            },
            "description": "Payment description"
        }]
    })

    if payment.create():
        return payment
    else:
        raise ValueError(payment.error)

def execute_payment(payment_id, payer_id):
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return payment
    else:
        raise ValueError(payment.error)

