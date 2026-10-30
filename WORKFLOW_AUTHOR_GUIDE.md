# How to write a workflow

A workflow is a short file that tells the support engine how to handle one kind of customer problem. For example, what to do when someone asks for a refund.

You don't need to know how to code to write one. If you can fill in a form, you can do this.

All the workflow files are in the `workflows` folder. There's one file per problem.

## What goes in a workflow

Every workflow has the same 7 parts:

- **intent** - the short name of the problem, like `refund_request`. Use small letters and underscores, no spaces.
- **name** - the normal name people will see, like `Refund Request`.
- **self_service** - can the customer sort this out on their own? Write `true` for yes, `false` if a person needs to help.
- **team** - which team looks after this problem, like `Payments`.
- **help_article** - the help page the AI reads before it replies to the customer, like `refund_request.md`.
- **steps** - what to do, in order. Write them the way you'd explain it to a new person on the team.
- **escalate_when** - when to hand the ticket to someone more senior.

## Example 1 (YAML file)

This is what `refund_request.yaml` looks like:

```yaml
intent: refund_request
name: Refund Request
self_service: false
team: Payments
help_article: refund_request.md
steps:
  - Ask the customer for their order number
  - Ask the customer why they want a refund
  - Ask for proof, such as a photo of the item
escalate_when:
  - The customer disagrees with a refused refund
```

Things to watch out for:

- Each step goes on its own line and starts with a dash.
- Put 2 spaces before each dash.
- Don't let a step run onto a second line. If it's too long, split it into 2 steps.

## Example 2 (JSON file)

Some workflows are JSON files instead. Same information, just written a bit differently. This is `password_reset.json`:

```json
{
  "intent": "password_reset",
  "name": "Password Reset",
  "self_service": true,
  "team": "Accounts",
  "help_article": "password_reset.md",
  "steps": [
    "Send the customer a password reset link",
    "If the link fails, send a new one"
  ],
  "escalate_when": [
    "The customer no longer has access to their email"
  ]
}
```

Things to watch out for:

- Put words inside double quotes, like `"Accounts"`.
- Put a comma after each item, except the last one in a list.
- `true` and `false` don't need quotes.

The missing or extra comma is the mistake everyone makes, so check that first if something breaks.

## Changing a workflow

1. Open the file in a text editor (not Word).
2. Change what you need.
3. Check it (see the end of this guide).
4. Save it.

That's it. The support engine picks up the new version the next time it runs.

## Adding a new workflow

1. Copy a workflow that's close to what you want.
2. Rename the copy, for example `damaged_parcel.yaml`.
3. Fill in the 7 parts.
4. Write the help article for it and put it in the `help_articles` folder.
5. Ask an engineer to add the new problem to the database, so the engine knows it exists.

## Checking your file

Before you save, paste your file into a free checker:

- for YAML files: yamllint.com
- for JSON files: jsonlint.com

If it says the file is fine, you're done. If not, it tells you which line is wrong.
