# e-ticket_system

The platform allow users to view events and purchase online using their mobile devices. It also allows event organizers to create and manage events.

# Functionalities

* User Registration and Login
* Event Creation
* Event Search and Browse
* Ticket Purchase
* User Dashboard
* Admin Dashboard

## Table of Content
* [Environment](#environment)
* [Directory Structure](#directory-structure)
* [File Descriptions](#file-descriptions)
* [Bugs](#bugs)
* [Authors](#authors)
* [License](#license)

## Environment
This project is tested on Ubuntu 20.04 LTS using python3 (version 3.8.10)

# Directory Structure

e-ticket_system/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── events.py
│   ├── tickets.py
│   ├── paypal.py
│   ├── users.py
│   ├── routes.py
│   └── README.md
├── db.py
├── db_setup.sql
├── dir_structure.sh
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── bootstrap.css
│   ├── js/
│   │   ├── main.js
│   │   └── jquery.js
│   └── images/
│       ├── logo.png
│       └── banner.png
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── home.html
│   ├── register.html
│   ├── event_details.html
│   ├── events.html
│   ├── purchase_confirmation.html
│   ├── purchase_error.html
│   └── tickets.html
├── tests/
│   ├── __init__.py
│   ├── auth_test.py
│   ├── events_test.py
│   ├── tickets_test.py
│   └── users_test.py
├── requirements.txt
├── README.md
└── run.py

## File Descriptions

[run.py](run.py) - entry point to the system
[requirements.txt](requirements.txt) - Lists all the required modules and packeges to run the system
[db.py](db.py) - Contains all the functions to create and access mySQL database
[db_setup.sql](db_setup.sql) - contains the required mySQL commands to create the database and tables

#### `app/` directory contains classes used for this project:
[__init__.py](/app/__init__.py) - Initialization file
[auth.py](/app/auth.py) - This module handles user authentication and authorization. It could contain functions for registering new users, logging in and out, and verifying user credentials.

[events.py](/app/events.py) - This module handles events. It contain functions for creating, updating, and deleting events, as well as retrieving event details.

[tickets.py](/app/tickets.py) - This module handles tickets. It could contain functions for creating and retrieving tickets, as well as cancelling tickets.

[paypal.py](/app/paypal.py) - This module handles payment processing. It contains functions for processing payments and refunding payments.

[users.py](/app/users.py) - This module handles user management. It contain functions for retrieving and updating user details.

[routes.py](/app/routes.py) - This module define API routes. It contain Flask route definitions, which specify what happens when a user visits a certain URL.

#### `static/` directory contains css and js scripts used for this project

#### `/tests` directory contains all unit test cases for this project:
[auth_test.py](/tests/auth_test) - Test the auth module
[tickets_test.py](/tests/tickets_test.py) - test tickets module
[user_test.py](/tests/ticket_test.py) - test user module

## Authors
Calvin Sharara - [Github](https://github.com/calvean)

## License
Public Domain. No copy write protection.
