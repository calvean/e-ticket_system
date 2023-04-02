from flask import Flask, jsonify, request, session, render_template, flash, redirect, url_for
import event
import ticket
import user
import paypal
import db

app = Flask(__name__)
app.secret_key = 'supersecretkey'


@app.route('/')
def home():
    conn = db.create_connection()
    cursor = conn.cursor()

    # Fetch 5 most recent events and their ticket price
    query = """
        SELECT id, name, description, date, price
        FROM events
        ORDER BY date DESC
        LIMIT 5
    """
    cursor.execute(query)
    events = cursor.fetchall()

    # Close database connection
    conn.close()

    # Pass user name to template context
    user_name = session.get('user_name')
    return render_template('home.html', events=events, user_name=user_name)


@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'GET':
        events = event.get_events()
        return jsonify(events)
    elif request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        price = request.form['price']
        description = request.form['description']
        event_info = event.create_event(name, date, time, location, price, description)
        return jsonify(event_info)

@app.route('/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def event_detail(event_id):
    if request.method == 'GET':
        event_info = event.get_event(event_id)
        if not event_info:
            return jsonify({'error': 'Event not found'}), 404
        return jsonify(event_info)
    elif request.method == 'PUT':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        price = request.form['price']
        description = request.form['description']
        event_info = event.update_event(event_id, name, date, time, location, price, description)
        return jsonify(event_info)
    elif request.method == 'DELETE':
        event_info = event.delete_event(event_id)
        return jsonify(event_info)

@app.route('/events/<int:event_id>/tickets', methods=['POST'])
def purchase_tickets(event_id):
    email = request.form['email']
    quantity = int(request.form['quantity'])
    event_info = event.get_event(event_id)
    if not event_info:
        return jsonify({'error': 'Event not found'}), 404
    total_price = event_info['price'] * quantity
    ticket_info = ticket.create_ticket(event_id, email, quantity, total_price)
    paypal_info = paypal.create_paypal_payment(ticket_info['id'], total_price)
    return jsonify(paypal_info)

@app.route('/users/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Create user in database
        user_info = user.create_user(name, email, password)
        print(user_info)
        flash(user_info['message'], 'error' if user_info['status_code'] == 409 else 'success')
        if user_info['status_code'] == 200:
            session['user_id'] = user_info['id']
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/users/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_info = user.get_user_by_email(email)
        if not user_info or not user.verify_password(user_info['password'], password):
            flash('Invalid email or password', 'error')
        else:
            session['user_id'] = user_info['id']
            session['user_name'] = user_info['name']
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/users/logout', methods=['POST'])
def logout_user():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    app.run(debug=True)

