#!/usr/bin/python3
""" Event Module """
from datetime import datetime
from database import (
    create_connection,
    create_tables,
    insert_event,
    insert_user,
    check_database,
    )


class Event:
    """ Event Class """

    def __init__(
            self, id=None, name=None, description=None,
            date=None, price=None, venue=None,
            category=None, image=None):
        """ Initialization """
        self.id = id
        self.name = name
        self.description = description
        self.date = date
        self.price = price
        self.venue = venue
        self.category = category
        self.image = image

    def save(self):
        """ Save Function """
        conn = create_connection()
        cursor = conn.cursor()

        if self.id is None:
            query = """
                INSERT INTO events (
                    name, description, date, price, venue, category, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                self.name, self.description, self.date, self.price,
                self.venue, self.category, self.image
            )
        else:
            query = """
                UPDATE events SET name=%s, description=%s, date=%s, price=%s, venue=%s, category=%s, image=%s
                WHERE id=%s
            """
            values = (
                self.name, self.description, self.date, self.price,
                self.venue, self.category, self.image, self.id
            )

        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def __str__(self):
        """ Return String representation """
        return f"{self.name} ({self.date}): {self.description[:50]}..."

    def __repr__(self):
        """ Return representation """
        return f"Event(id={self.id}, name={self.name}, date={self.date}, price={self.price})"

    def delete(self):
        """ Delete function """
        conn = create_connection()
        cursor = conn.cursor()

        query = "DELETE FROM events WHERE id=%s"
        cursor.execute(query, (self.id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_all(cls):
        """ Class method to Return all events """
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM events"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        events = []
        for row in rows:
            event = cls(*row)
            events.append(event)

        return events

    @classmethod
    def get_by_id(cls, id):
        """ Class Method to get events by id """
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM events WHERE id=%s"
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        conn.close()

        if row is not None:
            return cls(*row)
        else:
            return None

    @classmethod
    def get_upcoming(cls):
        """ Method to return all upcoming events """
        conn = create_connection()
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "SELECT * FROM events WHERE date >= %s"
        cursor.execute(query, (now,))
        rows = cursor.fetchall()
        conn.close()

        events = []
        for row in rows:
            event = cls(*row)
            events.append(event)

        return events

    @classmethod
    def get_by_category(cls, category):
        """" Method to return events by category """
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM events WHERE category=%s"
        cursor.execute(query, (category,))
        rows = cursor.fetchall()
        conn.close()

        events = []
        for row in rows:
            event = cls(*row)
            events.append(event)

        return events

    @classmethod
    def get_by_user_id(cls, user_id):
        """ Class Method to return events by user id """
        conn = create_connection()
        cursor = conn.cursor()

        query = """
            SELECT e.*
            FROM events e
            INNER JOIN tickets t ON e.id = t.event_id
            WHERE t.user_id = %s
            ORDER BY e.date DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        events = []
        for row in rows:
            event = Event(*row)
            events.append(event)

        return events
