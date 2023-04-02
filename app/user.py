#!/usr/bin/python3
import db
import bcrypt

# user.py

def create_user(name, email, password):
    conn = db.create_connection()
    cursor = conn.cursor()

    # Check if user already exists
    query = "SELECT id FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    if result:
        conn.close()
        return {'message': 'User with that email already exists', 'status_code': 409}

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    print("Hashed Password: ", hashed_password)

    # Insert new user into database
    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    values = (name, email, hashed_password)
    cursor.execute(query, values)
    conn.commit()

    # Fetch user from database by email
    query = "SELECT id, name, email, password FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    # Close database connection
    conn.close()

    # Return user data as a dictionary
    if result:
        return {'message': 'User created successfully!', 'status_code': 200, 'id': result[0]}
    else:
        return {'message': 'Error creating user', 'status_code': 500}


def get_user_by_email(email):
    conn = db.create_connection()
    cursor = conn.cursor()

    # Fetch user from database by email
    query = "SELECT id, name, email, password FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    # Close database connection
    conn.close()

    # Return user data as a dictionary
    if result:
        return {'id': result[0], 'name': result[1], 'email': result[2], 'password': result[3]}
    else:
        return None

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

