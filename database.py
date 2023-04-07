#!/usr/bin/python3
import mysql.connector
import hashlib

DATABASE_NAME = 'tickets'

def create_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='test',
            password='pswd',
            database=DATABASE_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(err)
        print(f"Error connecting to MySQL database: {err}")
        return None

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create events table
    query = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            date TIMESTAMP NOT NULL,
            price FLOAT NOT NULL,
            venue VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            image VARCHAR(255)
        )
    """

    cursor.execute(query)

    # Create users table
    query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') DEFAULT 'user'
        )
    """
    cursor.execute(query)

    # Create tickets table
    query = """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            event_id INTEGER,
            user_id INTEGER,
            quantity INTEGER,
            price FLOAT,
            status VARCHAR(255) NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    cursor.execute(query)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def insert_event(name, description, date, price, venue, category, image=None):
    conn = create_connection()
    cursor = conn.cursor()

    # Insert event into events table
    query = """
        INSERT INTO events (name, description, date, price, venue, category, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, description, date, price, venue, category, image))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def insert_user(name, email, password, role='user'):
    conn = create_connection()
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Insert user into users table
    query = """
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (name, email, hashed_password, role))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def insert_ticket(event_id, user_id, quantity, price, status):
    conn = create_connection()
    cursor = conn.cursor()

    # Insert ticket into ticket table
    query = """
        INSERT INTO tickets (event_id, user_id, quantity, price, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (event_id, user_id, quantity, price, status))

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Create a function to check if the database is working
def check_database():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Test the connection by selecting data from the events table
        query = "SELECT * FROM events"
        cursor.execute(query)
        events_result = cursor.fetchall()

        # If the events result is empty, the database is empty
        if not events_result:
            # Insert a sample event
            insert_event(
                name="Sample Event",
                description="This is a sample event",
                date="2023-04-15 12:00:00",
                price=10.0,
                venue="Sample Venue",
                category="Sample Category",
                image=None
            )
            print("Sample event added to the database")

        # Test the connection by selecting data from the users table
        query = "SELECT * FROM users"
        cursor.execute(query)
        users_result = cursor.fetchall()

        # If the users result is empty, the database is empty
        if not users_result:
            # Insert a sample user
            insert_user(
                name="Sample User",
                email="sample@example.com",
                password="password"
            )
            print("Sample user added to the database")
            # Insert a admin
            insert_user(
                name="admin",
                email="admin@example.com",
                password="admin",
                role="admin"
            )
            print("admin added to the database")

        # Close the connection
        conn.close()

        # Print a message to the console
        if not events_result or not users_result:
            print("Sample data added to the database")
        else:
            print("Database connection successful")

    except mysql.connector.Error as error:
        # If the error is related to the database not existing, create it and create the tables
        if error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            conn = mysql.connector.connect(
                host='localhost',
                user='test',
                password='pswd'
            )
            cursor = conn.cursor()

            # Create the database and switch to it
            cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
            cursor.execute(f"USE {DATABASE_NAME}")

            # Create the tables
            create_tables()

            # Close the connection
            conn.close()

            # Insert sample data
            insert_event(
                name="Eventing Launch",
                description="Official launch of my Eventing App",
                date="2023-04-15 12:00:00",
                price=10.0,
                venue="Harare, Zimbabwe",
                category="Online",
                image=None
            )
            insert_user(
                name="Sample User",
                email="sample@example.com",
                password="password"
            )
            insert_user(
                name="admin",
                email="admin@example.com",
                password="admin",
                role="admin"
            )
            print("Sample data added to the database")

        else:
            print(f"Database connection error: {error}")

