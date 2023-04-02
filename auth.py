#!/usr/bin/python3
import db
from flask import jsonify, request, session


def login():
    conn = db.create_connection()
    cursor = conn.cursor()
    data = request.get_json()
    email = data['email']
    password = data['password']
    cursor.execute('''SELECT * FROM users WHERE email = %s AND password = %s''', (email, password))
    user = cursor.fetchone()
    if user:
        session['user_id'] = user[0]
        return jsonify({'message': 'User logged in successfully!'})
    cursor.execute('''SELECT * FROM admins WHERE email = %s AND password = %s''', (email, password))
    admin = cursor.fetchone()
    if admin:
        session['admin_id'] = admin[0]
        return jsonify({'message': 'Admin logged in successfully!'})
    return jsonify({'error': 'Invalid email or password'})

def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully!'})
