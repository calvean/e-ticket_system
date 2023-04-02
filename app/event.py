#!/usr/bin/python3
import db

# event.py

def create_event(name, date, time, location, price, description):
    conn = db.create_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO events (name, date, time, location, price, description) VALUES (%s, %s, %s, %s, %s, %s)", (name, date, time, location, price, description))
    conn.commit()

    event_id = cur.lastrowid

    cur.close()
    conn.close()

    return {"id": event_id, "name": name, "date": date, "time": time, "location": location, "price": price, "description": description}

def get_events():
    conn = db.create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events")
    rows = cur.fetchall()

    events = []
    for row in rows:
        event = {"id": row[0], "name": row[1], "date": row[2], "time": row[3], "location": row[4], "price": row[5], "description": row[6]}
        events.append(event)

    cur.close()
    conn.close()

    return events

def get_event(event_id):
    conn = db.create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    row = cur.fetchone()

    if not row:
        return None

    event = {"id": row[0], "name": row[1], "date": row[2], "time": row[3], "location": row[4], "price": row[5], "description": row[6]}

    cur.close()
    conn.close()

    return event

def update_event(event_id, name, date, time, location, price, description):
    conn = db.create_connection()
    cur = conn.cursor()

    cur.execute("UPDATE events SET name=%s, date=%s, time=%s, location=%s, price=%s, description=%s WHERE id=%s", (name, date, time, location, price, description, event_id))
    conn.commit()

    cur.close()
    conn.close()

    return {"id": event_id, "name": name, "date": date, "time": time, "location": location, "price": price, "description": description}

def delete_event(event_id):
    conn = db.create_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
    conn.commit()

    cur.close()
    conn.close()

    return {"id": event_id}

