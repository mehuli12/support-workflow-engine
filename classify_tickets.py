# Classify tickets that don't have an intent yet, using Claude.

from datetime import datetime
from getpass import getpass

import anthropic
import mysql.connector

MODEL = "claude-haiku-5-5"
HOW_MANY = 5  # 5 for a test run, 400 for everything

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getpass("MySQL password: "),
    database="support_engine",
)
cursor = connection.cursor()

# name -> id lookup, plus the list of intents we show Claude
cursor.execute("SELECT intent_id, intent_name, description FROM intents")
intent_ids = {}
intent_list = ""
for intent_id, intent_name, description in cursor.fetchall():
    intent_ids[intent_name] = intent_id
    intent_list += f"- {intent_name}: {description}\n"

cursor.execute("SELECT ticket_id, subject FROM tickets WHERE intent_id IS NULL LIMIT %s", (HOW_MANY,))
tickets = cursor.fetchall()

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY

for ticket_id, subject in tickets:
    prompt = f"""Classify this customer support ticket into one of these intents:

{intent_list}
Ticket: "{subject}"

Reply with the intent name only."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=20,
        thinking={"type": "disabled"},  # a one-word answer doesn't need thinking
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.content[0].text.strip()

    if answer not in intent_ids:
        print(f"Ticket {ticket_id}: unexpected answer '{answer}', skipped")
        continue

    cursor.execute("UPDATE tickets SET intent_id = %s WHERE ticket_id = %s", (intent_ids[answer], ticket_id))
    cursor.execute(
        "INSERT INTO ticket_events (ticket_id, event_type, occurred_at) VALUES (%s, 'classified', %s)",
        (ticket_id, datetime.now()),
    )
    connection.commit()  # per ticket, so a crash halfway doesn't lose anything
    print(f"Ticket {ticket_id}: {subject} -> {answer}")

connection.close()
