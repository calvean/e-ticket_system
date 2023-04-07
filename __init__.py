#!/usr/bin/python3
from flask import Flask
from database import create_connection, create_tables, insert_event, insert_user, check_database

UPLOAD_FOLDER = 'uploads'


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

check_database()
