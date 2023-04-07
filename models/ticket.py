from database import create_connection, create_tables, insert_event, insert_user, check_database

class Ticket:
    def __init__(self, id=None, event_id=None, user_id=None, quantity=None, price=None, status="Available"):
        self.id = id
        self.event_id = event_id
        self.user_id = user_id
        self.quantity = quantity
        self.price = price
        self.status = status

    def save(self):
        conn = create_connection()
        cursor = conn.cursor()

        if self.id is None:
            query = "INSERT INTO tickets (event_id, user_id, quantity, price, status) VALUES (%s, %s, %s, %s, %s)"
            values = (self.event_id, self.user_id, self.quantity, self.price, self.status)
        else:
            query = "UPDATE tickets SET event_id=%s, user_id=%s, quantity=%s, price=%s, status=%s WHERE id=%s"
            values = (self.event_id, self.user_id, self.quantity, self.price, self.status, self.id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete(self):
        conn = create_connection()
        cursor = conn.cursor()

        query = "DELETE FROM tickets WHERE id=%s"
        cursor.execute(query, (self.id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_all(cls):
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tickets"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        tickets = []
        for row in rows:
            ticket = cls(*row)
            tickets.append(ticket)

        return tickets

    @classmethod
    def get_by_id(cls, id):
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tickets WHERE id=%s"
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        conn.close()

        if row is not None:
            return cls(*row)
        else:
            return None

    @classmethod
    def get_by_event_id(cls, event_id):
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tickets WHERE event_id=%s"
        cursor.execute(query, (event_id,))
        rows = cursor.fetchall()
        conn.close()

        tickets = []
        for row in rows:
            print("Get event by id method:{}".format(row))
            ticket = cls(*row)
            tickets.append(ticket)

        return tickets

    @classmethod
    def get_by_user_id(cls, user_id):
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tickets WHERE user_id=%s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        tickets = []
        for row in rows:
            ticket = cls(*row)
            tickets.append(ticket)

        return tickets

    @classmethod
    def delete_by_event_id(cls, event_id):
        conn = create_connection()
        cursor = conn.cursor()

        query = "DELETE FROM tickets WHERE event_id=%s"
        cursor.execute(query, (event_id,))
        conn.commit()
        conn.close()

