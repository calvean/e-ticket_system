#!/usr/bin/python3
""" Starts a Flash Web Application """
from flask import Flask
from routes import *

app = Flask(__name__)
"""app.secret_key = 'secret'
"""

if __name__ == '__main__':
    app.run()
