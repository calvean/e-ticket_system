#!/usr/bin/python3
""" User Module """
from datetime import datetime
from database import (
    create_connection, create_tables,
    insert_event, insert_user, check_database)
import hashlib


class User:
    """ User Class """
    def __init__(self, id=None, name=None, email=None, password=None, role='user'):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def save(self):
        conn = create_connection()
        cursor = conn.cursor()

        if self.id is None:
            query = """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """
            values = (self.name, self.email, self.hash_password(self.password), self.role)
        else:
            query = """
                UPDATE users SET name=%s, email=%s, password=%s, role=%s
                WHERE id=%s
            """
            values = (self.name, self.email, self.hash_password(self.password), self.role, self.id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete(self):
        conn = create_connection()
        cursor = conn.cursor()

        query = "DELETE FROM users WHERE id=%s"
        cursor.execute(query, (self.id,))
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hash the password using SHA256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        """Check if the given password matches the hashed password"""
        hashed_password = self.hash_password(password)
        print(hashed_password)
        print(hashed_password == self.password)
        return hashed_password == self.password

    @classmethod
    def get_all(cls):
        """ Get all users """
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        users = []
        for row in rows:
            user = cls(*row)
            users.append(user)

        return users

    @classmethod
    def get_by_id(cls, id):
        """ Get user by id """
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE id=%s"
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        conn.close()

        if row is not None:
            return cls(*row)
        else:
            return None

    @classmethod
    def get_by_email(cls, email):
        """ Get user by email """
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE email=%s"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        conn.close()
        print(row)
        if row is not None:
            return cls(*row)
        else:
            return None

    @classmethod
    def update_role(cls, id, role):
        """ update user role """
        conn = create_connection()
        cursor = conn.cursor()

        query = "UPDATE users SET role=%s WHERE id=%s"
        cursor.execute(query, (role, id))

        conn.commit()
        conn.close()
