from datetime import datetime
from database import create_connection, create_tables, insert_event, insert_user, check_database


class Event:
    def __init__(
        self, id=None, name=None, description=None, date=None, price=None,
        venue=None, category=None, image=None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.date = date
        self.price = price
        self.venue = venue
        self.category = category
        self.image = image

    def save(self):
        conn = create_connection()
        cursor = conn.cursor()

        if self.id is None:
            query = """
                INSERT INTO events (name, description, date, price, venue, category, image)
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

    def delete(self):
        conn = create_connection()
        cursor = conn.cursor()

        query = "DELETE FROM events WHERE id=%s"
        cursor.execute(query, (self.id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_all(cls):
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

