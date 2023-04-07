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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


""" Authentication Routes """

""" User Registration """
@app.route('/users/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user is already registered
        if User.get_by_email(email) is not None:
            print(User.get_by_email(email))
            flash('User already exists', 'error')
            return render_template('login.html')
        
        role = 'user'
        user = User(name=name, email=email, password=password, role=role)
        user.save()
        print(user)
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('home'))
    else:
        return render_template('register.html')

""" User login route """
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_by_email(email)
        print(user)
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

""" Logout User/Admin """
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


""" User Routes """

"""Route to User Home """
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_user'))

    events = Event.get_all()
    print(events)
    user = User.get_by_id(session['user_id'])
    return render_template('dashboard.html', events=events, user=user)


""" Admin Routes """

""" Admin Home Route """
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_user'))
    user = User.get_by_id(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('home'))
    # Retrieve data for admin dashboard
    users = User.get_all()
    events = Event.get_all()

    tickets = Ticket.get_all()
    
    # Get ticket count for each event
    ticket_counts = {}
    ticket_sold = {}
    for event in events:
        ticket_counts[event.id] = get_ticket_count(event.id)[0]
        ticket_sold[event.id] = get_ticket_count(event.id)[1]
        print("Event_id:{}".format(event.id))
    return render_template('admin.html', users=users, events=events, user=user, ticket_counts=ticket_counts, ticket_sold=ticket_sold)

""" Admin View Tickets """
@app.route('/admin/view_tickets/<int:event_id>')
def view_tickets(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login_user'))
    user = User.get_by_id(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('home'))
    event = Event.get_by_id(event_id)
    tickets = Ticket.get_by_event_id(event_id)
    ticket_count = sum(ticket.event_id for ticket in tickets)
    return render_template('view_tickets.html', event=event, ticket_count=ticket_count, tickets=tickets)

""" Admin Add New Tickets """
@app.route('/admin/events/<int:event_id>/tickets/new', methods=['GET', 'POST'])
def new_ticket(event_id):
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

""" Delete  a Ticket for an Event """ 
@app.route('/admin/tickets/<int:event_id>/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket(ticket_id, event_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    ticket = Ticket.get_by_id(ticket_id)
    if ticket is None:
        return redirect('/admin')
    ticket.delete()
    return redirect(url_for('view_tickets', event_id=event_id))

""" Delete all tickets for an event """
@app.route('/tickets/<int:event_id>/delete', methods=['POST'])
def delete_all_tickets(event_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    tickets = Ticket.get_by_event_id(event_id)
    for ticket in tickets:
        ticket.delete()
    return redirect(url_for('view_tickets', event_id=event_id))


""" Admin Create An Event """
@app.route('/admin/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
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

        print("Event Date Time: {}".format(event_date_time))
        event = Event(name=name, description=description, date=event_date_time_str, price=price, venue=venue, category=category, image=image)
        event.save()
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    else:
        return render_template('create_event.html')

""" Edit Event """
@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        event.name = request.form['name']
        event.description = request.form['description']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d %H:%M:%S')
        event.price = float(request.form['price'])
        event.venue = request.form['venue']
        event.category = request.form['category']
        event.image = request.form['image']
        event.save()
        return redirect(url_for('view_events',event_id=event.id))
    else:
        return render_template('edit_event.html', event=event)

""" Admin Delete Event """
@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect(url_for('admin_dashboard'))
    event.delete()
    return redirect(url_for('admin_dashboard'))

""" Update user Info """
@app.route('/admin/users/<int:user_id>', methods=['POST'])
def update_user(user_id):
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
    return redirect('/users/{}'.format(user.id))

""" Admin Delete Users"""
@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        abort(403)
    print(user_id)
    user = User.get_by_id(user_id)
    if user is not None:
        user.delete()
    return redirect(request.referrer)

""" Update User Role """
@app.route('/admin/users/<int:user_id>/toggle-role', methods=['POST'])
def update_role(user_id):
    if session.get('role') != 'admin':
        abort(403)

    user = User.get_by_id(user_id)
    if user is None:
        abort(404)

    new_role = 'user' if user.role == 'admin' else 'admin'
    User.update_role(user_id, new_role)

    return redirect(url_for('admin_dashboard'))

@app.route('/users/events/<int:event_id>')
def event_detail(event_id):
    event = Event.get_by_id(event_id)
    return render_template('event_detail.html', event=event)


""" Get The number of Tickets for an event """
def get_ticket_count(event_id):
    tickets = Ticket.get_by_event_id(event_id)
    sold_tickets = 0
    ticket_count = []
    for ticket in tickets:
        print("tickets:{}".format(ticket_count))
        if ticket.status == 'Sold':
            sold_tickets += 1
    total_tickets = len(tickets)
    ticket_count = [total_tickets, sold_tickets ]
    return ticket_count


"""Check if the file type is allowed """
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""" Upload a file for an event """
def upload_file():
    # Check if the post request has the file part
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['image']
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        # Secure the filename to prevent malicious injections
        filename = secure_filename(file.filename)
        # Save the file to the upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(filename)
        # Return the filename
        return filename

@app.route('/events/<int:event_id>/buy_tickets', methods=['GET', 'POST'])
def buy_tickets(event_id):
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/')
    
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect('/login')
        user = User.get_by_id(session['user_id'])
        if user is None:
            return redirect('/login')
        
        quantity = int(request.form['quantity'])
        if quantity <= 0:
            return render_template('buy_tickets.html', event=event, error='Invalid quantity')
        
        total_price = quantity * event.price
        
        try:
            payment = create_payment(total_price, {
                "return_url": url_for('buy_tickets_confirm', event_id=event_id, _external=True),
                "cancel_url": url_for('buy_tickets', event_id=event_id, _external=True)
            })
            
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
            
            return render_template('buy_tickets.html', event=event, error='Payment error')
        
        except ValueError as e:
            return render_template('buy_tickets.html', event=event, error=str(e))
    
    else:
        return render_template('buy_tickets.html', event=event)
        
@app.route('/events/<int:event_id>/buy_tickets/confirm')
def buy_tickets_confirm(event_id):
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/')
    
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    if user is None:
        return redirect('/login')
    
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
    return redirect('/events/{}'.format(event_id))

""" Event Tickets """
@app.route('/user/events/<int:event_id>/tickets')
def event_tickets(event_id):
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/')
    tickets = event.get_tickets()
    return render_template('event_tickets.html', event=event, tickets=tickets)

""" Create tickets for an event """
def create_tickets_for_event(event_id, quantity):
    # Get the event and its price
    event = Event.get_by_id(event_id)
    price = event.price
    
    print("Event_id from create ticket fun:{}".format(event.id))
    print("Event_price from create ticket fun:{}".format(event.price))
    # Create the tickets
    tickets = []
    for i in range(quantity):
        ticket = Ticket(event_id=event_id, price=price)
        ticket.save()
        tickets.append(ticket)

    return tickets



@app.route('/tickets/<int:ticket_id>')
def ticket_detail(ticket_id):
    ticket = Ticket.get_by_id(ticket_id)
    if ticket is None:
        return redirect('/')
    return render_template('ticket_detail.html', ticket=ticket)

@app.route('/tickets/<int:ticket_id>/edit', methods=['GET', 'POST'])
def edit_ticket(ticket_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    ticket = Ticket.get_by_id(ticket_id)
    if ticket is None:
        return redirect('/')
    if request.method == 'POST':
        ticket.quantity = int(request.form['quantity'])
        ticket.price = float(request.form['price'])
        ticket.save()
        return redirect(f'/tickets/{ticket.id}')
    else:
        return render_template('edit_ticket.html', ticket=ticket)


@app.route('/users', methods=['GET'])
def get_users():
    if session.get('role') != 'admin':
        abort(403)
    users = User.get_all()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        return redirect('/users')
    return render_template('user.html', user=user)

@app.route('/users/email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    user = User.get_by_email(email)
    if user is None:
        return redirect('/users')
    return render_template('user.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
