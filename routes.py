#!/usr/bin/python3
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

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_user'))

    events = Event.get_all()
    print(events)
    user = User.get_by_id(session['user_id'])
    return render_template('dashboard.html', events=events, user=user)


@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.get_by_id(event_id)
    return render_template('event_detail.html', event=event)

@app.route('/register', methods=['GET', 'POST'])
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
        return redirect('/')
    else:
        return render_template('register.html')

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
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')


@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.get_by_id(session['user_id'])
    if user.role != 'admin':
        return redirect('/')
    # Retrieve data for admin dashboard
    users = User.get_all()
    events = Event.get_all()
    tickets = Ticket.get_all()
    return render_template('admin.html', users=users, events=events, user=user)

def get_ticket_count(event_id):
    tickets = Ticket.get_by_event_id(event_id)
    count = 0
    for ticket in tickets:
        count += ticket.quantity
    return count

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Check if the file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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

@app.route('/create_event', methods=['GET', 'POST'])
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
        return redirect('/admin')

    else:
        return render_template('create_event.html')

@app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/')
    if request.method == 'POST':
        event.name = request.form['name']
        event.description = request.form['description']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d %H:%M:%S')
        event.price = float(request.form['price'])
        event.venue = request.form['venue']
        event.category = request.form['category']
        event.image = request.form['image']
        event.save()
        return redirect('/events/{}'.format(event.id))
    else:
        return render_template('edit_event.html', event=event)

@app.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/admin')
    event.delete()
    return redirect('/admin')

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


@app.route('/events/<int:event_id>/tickets')
def event_tickets(event_id):
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/')
    tickets = event.get_tickets()
    return render_template('event_tickets.html', event=event, tickets=tickets)

def create_tickets_for_event(event_id, quantity):
    # Get the event and its price
    event = Event.get_by_id(event_id)
    price = event.price

    # Create the tickets
    tickets = []
    for i in range(quantity):
        ticket = Ticket(event_id=event_id, price=price)
        ticket.save()
        tickets.append(ticket)

    return tickets

@app.route('/events/<int:event_id>/tickets/new', methods=['GET', 'POST'])
def new_ticket(event_id):
    if 'user_id' not in session:
        return redirect('/login')
    user = User.get_by_id(session['user_id'])
    if user is None:
        return redirect('/')
    event = Event.get_by_id(event_id)
    if event is None:
        return redirect('/')
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        if quantity > 0:
            ticket = create_tickets_for_event(event_id, quantity)
            return redirect('/admin')
        else:
            return render_template('new_ticket.html', event=event, error='Invalid quantity')
    else:
        return render_template('new_ticket.html', event=event)

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

@app.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket(ticket_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/')
    ticket = Ticket.get_by_id(ticket_id)
    if ticket is None:
        return redirect('/')
    ticket.delete()
    return redirect('/')

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

@app.route('/users/<int:user_id>', methods=['POST'])
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

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        abort(403)
    print(user_id)
    user = User.get_by_id(user_id)
    if user is not None:
        user.delete()
    return redirect(request.referrer)

@app.route('/users/<int:user_id>/toggle-role', methods=['POST'])
def update_role(user_id):
    if session.get('role') != 'admin':
        abort(403)

    user = User.get_by_id(user_id)
    if user is None:
        abort(404)

    new_role = 'user' if user.role == 'admin' else 'admin'
    User.update_role(user_id, new_role)

    return redirect('/admin')



if __name__ == '__main__':
    app.run(debug=True)
