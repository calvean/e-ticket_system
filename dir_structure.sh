#!/bin/bash

# Create main directory
mkdir online-ticket-system
cd online-ticket-system

# Create app directory and files
mkdir app
touch app/__init__.py
touch app/auth.py
touch app/events.py
touch app/tickets.py
touch app/users.py

# Create db.py file
touch db.py

# Create static directory and subdirectories
mkdir static
mkdir static/css
mkdir static/js
mkdir static/images

# Create static files
touch static/css/style.css
touch static/css/bootstrap.css
touch static/js/main.js
touch static/js/jquery.js
touch static/images/logo.png
touch static/images/banner.png

# Create templates directory and files
mkdir templates
touch templates/base.html
touch templates/login.html
touch templates/register.html
touch templates/event_details.html
touch templates/events.html
touch templates/purchase_confirmation.html
touch templates/purchase_error.html

# Create tests directory and files
mkdir tests
touch tests/__init__.py
touch tests/auth_test.py
touch tests/events_test.py
touch tests/tickets_test.py
touch tests/users_test.py

# Create requirements file
touch requirements.txt

# Create run.py file
touch run.py

# Print completion message
echo "Directory structure created successfully!"

