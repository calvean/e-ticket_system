#!/usr/bin/python3
from flask import Flask
from database import create_connection, create_tables, insert_event, insert_user, check_database



insert_user(
    name="admin",
    email="admin@example.com",
    password="admin",
    role="admin"
)
print("admin added to the database")


