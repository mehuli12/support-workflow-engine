# Draft replies for a few open tickets, using each ticket's workflow file and help article.
# Nothing is saved yet. It prints what the engine would do with each ticket.

from getpass import getpass

import anthropic
import mysql.connector
import yaml

MODEL = "claude-haiku-5-5"
HOW_MANY = 3

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getpass("MySQL password: "),
    database="support_engine",
)
cursor = connection.cursor()

# A few random open tickets, with the customer's name and the ticket's workflow file
cursor.execute(
    """SELECT ticket_id, customer_name, subject, config_file
       FROM tickets
       JOIN customers USING (customer_id)
       JOIN workflows USING (intent_id)
       WHERE status = 'open'
       ORDER BY RAND()
       LIMIT %s""",
    (HOW_MANY,),
)
tickets = cursor.fetchall()

client = anthropic.Anthropic()

for ticket_id, customer_name, subject, config_file in tickets:
    with open(config_file) as file:
        workflow = yaml.safe_load(file)  # reads JSON files too, because JSON is valid YAML

    with open("help_articles/" + workflow["help_article"]) as file:
        article = file.read()

    first_name = customer_name.split()[0]
    prompt = f"""You are a customer support agent. Write a short, friendly reply to this customer.
Use only the information in the help article below. If it doesn't answer their question,
say that a member of the team will follow up.

Customer name: {first_name}
Customer message: "{subject}"

Help article:
{article}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    draft = response.content[0].text.strip()

    # The workflow file decides what happens next
    if workflow["self_service"]:
        next_step = "send the reply straight away"
    else:
        next_step = f"send to the {workflow['team']} team for an agent to check"

    print(f"Ticket {ticket_id}: {subject}")
    print(f"Workflow: {workflow['name']}  |  Next step: {next_step}")
    print()
    print(draft)
    print("-" * 60)

connection.close()
