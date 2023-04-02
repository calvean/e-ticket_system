#!/usr/bin/python3
import mysql.connector

def create_connection():
    # Connect to MySQL server
    return mysql.connector.connect(
        host='localhost',
        user='test',
        password='pswd',
        database='tickets'
    )
