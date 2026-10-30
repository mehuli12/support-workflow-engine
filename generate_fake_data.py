# Fills the support_engine database with fake customers, tickets and ticket events.
# Run it once, after the tables, intents and workflows have been created.

import random
from datetime import datetime, timedelta
from getpass import getpass

import mysql.connector

NUMBER_OF_CUSTOMERS = 200
NUMBER_OF_TICKETS = 2000

FIRST_NAMES = ["Aisha", "Liam", "Priya", "Noah", "Sofia", "Arjun", "Emma", "Omar", "Chloe", "Rahul"]
LAST_NAMES = ["Smith", "Patel", "Jones", "Khan", "Brown", "Das", "Taylor", "Singh", "Roy", "Ghosh"]
COUNTRIES = ["United Kingdom", "India", "United States", "Germany", "Canada"]
CHANNELS = ["email", "chat", "app"]

# What a customer might write for each type of problem
SUBJECTS = {
    "order_status": ["Where is my order?", "Has my order shipped yet?"],
    "delivery_delay": ["My delivery is late", "Parcel stuck in transit"],
    "refund_request": ["I would like a refund", "Please refund my last order"],
    "billing_dispute": ["I was charged twice", "Wrong amount on my bill"],
    "password_reset": ["I forgot my password", "Reset link is not working"],
    "account_access": ["My account is locked", "Cannot access my account"],
    "product_defect": ["Item arrived broken", "Product stopped working"],
    "cancel_subscription": ["Please cancel my subscription", "How do I stop my plan?"],
    "general_enquiry": ["Question about your service", "Do you ship abroad?"],
}


def create_customers(cursor):
    for number in range(1, NUMBER_OF_CUSTOMERS + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = first_name + " " + last_name
        email = f"{first_name}.{last_name}{number}@example.com".lower()  # the number makes each email unique
        country = random.choice(COUNTRIES)
        signup_date = datetime.now() - timedelta(days=random.randint(30, 730))

        cursor.execute(
            "INSERT INTO customers (customer_name, email, country, signup_date) VALUES (%s, %s, %s, %s)",
            (name, email, country, signup_date.date()),
        )


def add_event(cursor, ticket_id, event_type, occurred_at):
    cursor.execute(
        "INSERT INTO ticket_events (ticket_id, event_type, occurred_at) VALUES (%s, %s, %s)",
        (ticket_id, event_type, occurred_at),
    )


def create_ticket(cursor, customer_ids, intents):
    customer_id = random.choice(customer_ids)
    intent_id, intent_name, target_hours = random.choice(intents)
    subject = random.choice(SUBJECTS[intent_name])
    channel = random.choice(CHANNELS)
    created_at = datetime.now() - timedelta(days=random.randint(7, 90), hours=random.randint(0, 23))

    # 15% of tickets are new and not classified yet: no intent, no deadline, still open
    if random.random() < 0.15:
        intent_id = None
        resolution_due_at = None
        status = "open"
    else:
        resolution_due_at = created_at + timedelta(hours=target_hours)
        status = random.choices(["open", "in_progress", "resolved", "escalated"], weights=[15, 15, 60, 10])[0]

    # Resolved tickets take between 1 hour and twice the target time, so some are late
    resolved_at = None
    if status == "resolved":
        resolved_at = created_at + timedelta(hours=random.randint(1, target_hours * 2))

    cursor.execute(
        """INSERT INTO tickets
           (customer_id, intent_id, subject, channel, status, created_at, resolution_due_at, resolved_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (customer_id, intent_id, subject, channel, status, created_at, resolution_due_at, resolved_at),
    )
    ticket_id = cursor.lastrowid  # the ID MySQL just gave this ticket

    # Record what happened to the ticket, in order
    add_event(cursor, ticket_id, "created", created_at)
    if intent_id is not None:
        add_event(cursor, ticket_id, "classified", created_at + timedelta(minutes=1))
    if status in ["in_progress", "resolved", "escalated"]:
        add_event(cursor, ticket_id, "routed", created_at + timedelta(minutes=2))
    if status == "resolved":
        add_event(cursor, ticket_id, "resolved", resolved_at)
    if status == "escalated":
        add_event(cursor, ticket_id, "escalated", created_at + timedelta(hours=1))


def main():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=getpass("MySQL password: "),
        database="support_engine",
    )
    cursor = connection.cursor()

    # Stop if the data is already there, so running the script twice doesn't double it
    cursor.execute("SELECT COUNT(*) FROM tickets")
    if cursor.fetchone()[0] > 0:
        print("Tickets already exist, so nothing was added.")
        return

    create_customers(cursor)

    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT intent_id, intent_name, target_resolution_hours FROM intents")
    intents = cursor.fetchall()

    for _ in range(NUMBER_OF_TICKETS):
        create_ticket(cursor, customer_ids, intents)

    connection.commit()  # save everything in one go
    connection.close()
    print(f"Done: {NUMBER_OF_CUSTOMERS} customers and {NUMBER_OF_TICKETS} tickets added.")


main()
