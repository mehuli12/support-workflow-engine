# Test the classifier on messy, realistic tickets where we already know the right answer.
# Nothing is saved to the database. It prints the accuracy and every ticket it got wrong.

from getpass import getpass

import anthropic
import mysql.connector

MODEL = "claude-haiku-5-5"

# (what the customer wrote, the intent a support lead would pick)
TEST_TICKETS = [
    ("hey when is my stuff coming, ordered on tuesday", "order_status"),
    ("can u check if order 4471 has left the warehouse yet", "order_status"),
    ("what's the status of my order pls", "order_status"),
    ("parcel was meant to come friday, it's now wednesday", "delivery_delay"),
    ("courier says delivered but there's nothing here", "delivery_delay"),
    ("still waiting!! 2 weeks now, this is ridiculous", "delivery_delay"),
    ("want my money back for the jacket, doesn't fit", "refund_request"),
    ("changed my mind about the order, can I get a refund?", "refund_request"),
    ("how do I send something back and get refunded", "refund_request"),
    ("there's a £14.99 charge on my card I don't recognise", "billing_dispute"),
    ("you took payment twice for one order!!", "billing_dispute"),
    ("I cancelled last month but you still charged me", "billing_dispute"),
    ("forgot my login details", "password_reset"),
    ("the reset email never arrived", "password_reset"),
    ("how do I change my password", "password_reset"),
    ("it says my account is suspended?", "account_access"),
    ("too many wrong attempts and now I'm locked out", "account_access"),
    ("I think someone else is using my account", "account_access"),
    ("the kettle stopped heating after 2 days", "product_defect"),
    ("screen was cracked when I opened the box", "product_defect"),
    ("the charger gets really hot, is that safe?", "product_defect"),
    ("don't want the monthly box anymore", "cancel_subscription"),
    ("how do I end my membership", "cancel_subscription"),
    ("pls stop my plan from renewing", "cancel_subscription"),
    ("do you deliver to Ireland?", "general_enquiry"),
    ("what times is your support team available", "general_enquiry"),
    ("hi", "general_enquiry"),
    # Harder ones: a real support lead could argue either way
    ("item arrived broken and I want a refund", "product_defect"),
    ("order 5521 never came, I want my money back", "delivery_delay"),
    ("can't log in, it keeps saying wrong password", "password_reset"),
]

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getpass("MySQL password: "),
    database="support_engine",
)
cursor = connection.cursor()

# Same intent list the real classifier uses
cursor.execute("SELECT intent_name, description FROM intents")
intent_names = []
intent_list = ""
for intent_name, description in cursor.fetchall():
    intent_names.append(intent_name)
    intent_list += f"- {intent_name}: {description}\n"
connection.close()

client = anthropic.Anthropic()
correct = 0

for message, expected in TEST_TICKETS:
    # Same prompt as classify_tickets.py, so we test what we actually run
    prompt = f"""Classify this customer support ticket into one of these intents:

{intent_list}
Ticket: "{message}"

Reply with the intent name only."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=20,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.content[0].text.strip()

    if answer == expected:
        correct += 1
    else:
        print(f'Wrong: "{message}"')
        print(f"       expected {expected}, got {answer}")

print()
print(f"Accuracy: {correct} out of {len(TEST_TICKETS)} ({correct / len(TEST_TICKETS):.0%})")
