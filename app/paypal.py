#!/usr/bin/python3

# payment.py

import requests
import paypalrestsdk

paypal_config = {
    "mode": "sandbox",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
}

paypalrestsdk.configure(paypal_config)

def paypal_access_token():
    client_id = 'YOUR_CLIENT_ID'
    secret = 'YOUR_SECRET'
    url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
        'Authorization': f'Basic {base64.b64encode(f"{client_id}:{secret}".encode()).decode()}'
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        return None

    access_token = response.json()['access_token']

    return access_token

def create_paypal_payment(total_cost):
    url = 'https://api.sandbox.paypal.com/v1/payments/payment'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {paypal_access_token()}'
    }

    payload = {
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal'
        },
        'transactions': [
            {
                'amount': {
                    'total': total_cost,
                    'currency': 'USD'
                },
                'description': 'Ticket Purchase'
            }
        ],
        'redirect_urls': {
            'return_url': 'http://localhost:5000/paypal/execute',
            'cancel_url': 'http://localhost:5000/paypal/cancel'
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 201:
        return None

    payment_id = response.json()['id']

    return payment_id

