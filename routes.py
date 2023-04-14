#!/usr/bin/python3
""" Routes Module """
from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import datetime, time
from models.event import Event
from models.user import User
from models.ticket import Ticket
from models.paypal import create_payment, execute_payment
from database import create_connection, create_tables, insert_event, insert_user, check_database
from __init__ import app
import os
from werkzeug.utils import secure_filename
import re

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


""" Authentication Routes """


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """ User Registration """

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        """ Check if user is already registered """
        if User.get_by_email(email) is not None:
            flash('User already exists', 'error')
            return render_template('login.html')

        role = 'user'
        user = User(name=name, email=email, password=password, role=role)
        user.save()

        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('login_user'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ User login route """

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_by_email(email)

        if user is not None and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """ Logout User/Admin """

    session.clear()
    return redirect(url_for('home'))


@app.route('/')
def home():
    """Route to User Home """

    if 'user_id' not in session:
        return redirect(url_for('login_user'))

    events = Event.get_upcoming()
    event = Event.get_by_user_id(session['user_id'])
    user = User.get_by_id(session['user_id'])
    tickets = Ticket.get_by_user_id(session['user_id'])
    event_name = None
    if event:
        """ get the first event from the list """
        event = event[0]
        event_name = Event.get_by_id(event.event_id)

    return render_template('dashboard.html', events=events, myevents=event, tickets=tickets, event_name=event_name, user=user)


@app.route('/user/<int:user_id>/events')
def user_events(user_id):
    """ User events """

    if 'user_id' not in session:
        return redirect(url_for('login_user'))

    event = Event.get_by_user_id(session['user_id'])
    user = User.get_by_id(session['user_id'])

    return render_template('user_events.html', event=event, user=user)


@app.route('/user/<int:user_id>/tickets')
def user_tickets(user_id):
    """ User Tickets """

    if 'user_id' not in session:
        return redirect(url_for('login_user'))
    tickets = Ticket.get_by_user_id(session['user_id'])
    event = Event.get_by_user_id(session['user_id'])
    user = User.get_by_id(session['user_id'])

    return render_template('user_tickets.html', event=event, tickets=tickets, user=user)


""" Admin Routes """
@app.route('/admin')
def admin_dashboard():
    """ Admin Home Route """

    if 'user_id' not in session:
        return redirect(url_for('login_user'))
    user = User.get_by_id(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('home'))

    """ Retrieve data for admin dashboard """
    users = User.get_all()
    events = Event.get_all()

    tickets = Ticket.get_all()

    """ Get ticket count for each event """
    ticket_counts = {}
    ticket_sold = {}
    for event in events:
        ticket_counts[event.id] = get_ticket_count(event.id)[0]
        ticket_sold[event.id] = get_ticket_count(event.id)[1]

    return render_template('admin.html', users=users, events=events, user=user, ticket_counts=ticket_counts, ticket_sold=ticket_sold)


@app.route('/admin/<int:event_id>/view_tickets')
def view_tickets(event_id):
    """ Admin View Tickets """

    if 'user_id' not in session:
        return redirect(url_for('login_user'))
    user = User.get_by_id(session['user_id'])

    if user.role != 'admin':
        return redirect(url_for('home'))

    event = Event.get_by_id(event_id)
    tickets = Ticket.get_by_event_id(event_id)
    ticket_count = get_ticket_count(event_id)[0]

    return render_template('view_tickets.html', event=event, ticket_count=ticket_count, tickets=tickets)


@app.route('/admin/events/<int:event_id>/tickets/new', methods=['GET', 'POST'])
def new_ticket(event_id):
    """ Admin Add New Tickets """

    if 'user_id' not in session:
        return redirect(url_for('admin_dashboard'))
    user = User.get_by_id(session['user_id'])
    if user is None:
        return redirect(url_for('admin_dashboard'))
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        if quantity > 0:
            ticket = create_tickets_for_event(event_id, quantity)
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('new_ticket.html', event=event, error='Invalid quantity')
    else:
        return render_template('new_ticket.html', event=event)


@app.route('/admin/tickets/<int:event_id>/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket(ticket_id, event_id):
    """ Delete  a Ticket for an Event """

    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    ticket = Ticket.get_by_id(ticket_id)
    if ticket is None:
        return redirect(url_for('admin_dashboard'))
    ticket.delete()
    return redirect(url_for('view_tickets', event_id=event_id))


@app.route('/admin/tickets/<int:event_id>/delete', methods=['POST'])
def delete_all_tickets(event_id):
    """ Delete all tickets for an event """

    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    tickets = Ticket.get_by_event_id(event_id)
    for ticket in tickets:
        ticket.delete()
    return redirect(url_for('view_tickets', event_id=event_id))


@app.route('/admin/create_event', methods=['GET', 'POST'])
def create_event():
    """ Admin Create An Event """

    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time_str = request.form['time']
        price = float(request.form['price'])
        venue = request.form['venue']
        description = request.form['description']
        category = request.form['category']
        image = upload_file()

        event_datetime = datetime.strptime(date + ' ' + time_str, '%Y-%m-%d %H:%M')
        event_time = event_datetime.time()
        event_date_time = datetime.combine(event_datetime.date(), event_time)
        event_date_time_str = event_date_time.strftime('%Y-%m-%d %H:%M')

        event = Event(name=name, description=description, date=event_date_time_str, price=price, venue=venue, category=category, image=image)
        event.save()
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    else:
        return render_template('create_event.html')


@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    """ Edit Event """

    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        event.name = request.form['name']
        event.description = request.form['description']
        date = request.form['date']
        time_str = request.form['time']
        event.price = float(request.form['price'])
        event.venue = request.form['venue']
        event.category = request.form['category']

        image = upload_file()
        event.image = image

        event_datetime = datetime.strptime(date + ' ' + time_str, '%Y-%m-%d %H:%M')
        event_time = event_datetime.time()
        event_date_time = datetime.combine(event_datetime.date(), event_time)
        event_date_time_str = event_date_time.strftime('%Y-%m-%d %H:%M')

        event.date = event_date_time_str
        event.save()
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('edit_event.html', event=event)


@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    """ Admin Delete Event """

    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('admin_dashboard'))

    """ Delete any tickets associated with the event """
    tickets = Ticket.get_by_event_id(event_id)
    for ticket in tickets:
        ticket.delete()

    """ Delete the event itself """
    event.delete()

    return redirect(url_for('admin_dashboard'))


@app.route('/users/<int:user_id>', methods=['POST'])
def update_user(user_id):
    """ Update user Info """

    user = User.get_by_id(user_id)
    if user is None:
        return redirect('/users')
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user.name = name
    user.email = email
    user.password = password
    user.save()
    return redirect(request.referrer)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """ Admin Delete Users"""

    if session.get('role') != 'admin':
        abort(403)
    print(user_id)
    user = User.get_by_id(user_id)
    if user is not None:
        user.delete()
    return redirect(request.referrer)


@app.route('/admin/users/<int:user_id>/toggle-role', methods=['POST'])
def update_role(user_id):
    """ Update User Role """

    if session.get('role') != 'admin':
        abort(403)

    user = User.get_by_id(user_id)
    if user is None:
        abort(404)

    new_role = 'user' if user.role == 'admin' else 'admin'
    User.update_role(user_id, new_role)

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    """ Update User Role """

    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if User.get_by_email(email) is not None:
            flash('User already exists', 'error')
            return render_template('add_user.html')

        user = User(name=name, email=email, password=password, role=role)
        user.save()

        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('add_user.html')


@app.route('/user/<int:user_id>/profile', methods=['GET', 'POST'])
def user_profile(user_id):
    """ Upadate user information """

    if 'user_id' not in session:
        return redirect(url_for('login_user'))

    user = User.get_by_id(session['user_id'])

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        errors = []

        if not name:
            errors.append('Name is required.')

        if not email:
            errors.append('Email is required.')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append('Email is not valid.')

        if password:
            if len(password) < 6:
                errors.append('Password must be at least 6 characters long.')
            elif password != confirm_password:
                errors.append('Passwords do not match.')

        if errors:
            return render_template('user_profile.html', user=user, errors=errors)

        user.name = name
        user.email = email

        if password:
            user.hash_password(password)

        user.save()

        flash('Profile updated successfully.', 'success')
        return redirect(url_for('home'))

    return render_template('user_profile.html', user=user)


@app.route('/users/events/<int:event_id>')
def event_detail(event_id):
    """ Display Event Details """

    event = Event.get_by_id(event_id)
    user = User.get_by_id(session['user_id'])

    return render_template('event_details.html', event=event, user=user)


def get_ticket_count(event_id):
    """ Get The number of Tickets for an event """

    tickets = Ticket.get_by_event_id(event_id)
    sold_tickets = 0
    ticket_count = []
    for ticket in tickets:
        if ticket.status != 'Available':
            sold_tickets += 1
    total_tickets = len(tickets)
    ticket_count = [total_tickets, sold_tickets]

    return ticket_count


def allowed_file(filename):
    """Check if the file type is allowed """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file():
    """" Upload a file for an event """

    """ Check if the post request has the file part """
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['image']

    """ If the user does not select a file, the browser
     submits an empty file without a filename
     """
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return filename


@app.route('/users/events/<int:event_id>/buy_tickets', methods=['GET', 'POST'])
def buy_ticket(event_id):
    """ Function to buy a ticket """

    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('home'))

    ticket_count = get_ticket_count(event_id)
    total_tickets = ticket_count[0]
    sold_tickets = ticket_count[1]
    tickets_available = total_tickets - sold_tickets

    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login_user'))
        user = User.get_by_id(session['user_id'])
        if user is None:
            return redirect(url_for('login_user'))

        quantity = int(request.form['quantity'])
        if quantity <= 0:
            return render_template('buy_tickets.html', event=event, tickets_available=tickets_available, error='Invalid quantity')
        elif quantity > tickets_available:
            return render_template('buy_tickets.html', event=event, tickets_available=tickets_available, error='Not enough tickets available')

        total_price = quantity * event.price

        try:
            payment = create_payment(total_price, {
                "return_url": url_for('buy_tickets_confirm', event_id=event_id, _external=True),
                "cancel_url": url_for('buy_ticket', event_id=event_id, _external=True)
            })

            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)

            return render_template('buy_tickets.html', event=event, tickets_available=tickets_available, error='Payment error')

        except ValueError as e:
            return render_template('buy_tickets.html', event=event, tickets_available=tickets_available, error=str(e))

    else:
        return render_template('buy_tickets.html', event=event, tickets_available=tickets_available)


@app.route('/events/<int:event_id>/buy_tickets/confirm')
def buy_tickets_confirm(event_id):
    """ Confirm tickets """

    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('home'))

    if 'user_id' not in session:
        return redirect(url_for('login_user'))

    user = User.get_by_id(session['user_id'])
    if user is None:
        return redirect(url_for('login_user'))

    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    try:
        payment = execute_payment(payment_id, payer_id)
    except ValueError as e:
        return render_template('buy_tickets.html', event=event, error=str(e))

    for i in range(int(payment.transactions[0].item_list.items[0].quantity)):
        ticket = Ticket(event_id=event_id, user_id=user.id)
        ticket.save()

    flash('Payment successful!')
    return redirect(url_for('event_details', event_id=event_id))


@app.route('/user/events/<int:event_id>/tickets')
def event_tickets(event_id):
    """ Event Tickets """

    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('home'))
    tickets = event.get_tickets()
    return render_template('event_tickets.html', event=event, tickets=tickets)


def create_tickets_for_event(event_id, quantity):
    """ Create tickets for an event """

    event = Event.get_by_id(event_id)
    price = event.price

    tickets = []
    for i in range(quantity):
        ticket = Ticket(event_id=event_id, price=price)
        ticket.save()
        tickets.append(ticket)

    return tickets


if __name__ == '__main__':
    app.run(host='0.0.0.0')
