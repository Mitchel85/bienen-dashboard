---
name: agentmail
description: API-first email platform designed for AI agents. Create and manage dedicated email inboxes, send and receive emails programmatically, and handle email-based workflows with webhooks and real-time events. Use when you need to set up agent email identity, send emails from agents, handle incoming email workflows, or replace traditional email providers like Gmail with agent-friendly infrastructure.
requires:
  env:
    - AGENTMAIL_API_KEY
---

# AgentMail Skill

You can send and receive emails using the AgentMail API. Use the `exec` tool to run curl commands against the AgentMail API.

## API Base URL

```
https://api.agentmail.to/v0
```

## Authentication

Include your API key in the Authorization header:

```
Authorization: Bearer $AGENTMAIL_API_KEY
```

## Existing Inboxes (from TOOLS.md)

- **Mitch:** clawdia4me@agentmail.to
- **Maja:** clawdia4maja@agentmail.to  
- **Mario:** clawdia4mario@agentmail.to

These inboxes have already been created. Use their inbox IDs when sending/receiving emails.

## Common Operations

### List inboxes

```bash
curl -s -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  https://api.agentmail.to/v0/inboxes
```

### Create an inbox

```bash
curl -s -X POST -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Agent"}' \
  https://api.agentmail.to/v0/inboxes
```

### Send an email

```bash
curl -s -X POST -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Hello from OpenClaw",
    "text": "This email was sent by my AI assistant."
  }' \
  https://api.agentmail.to/v0/inboxes/{inbox_id}/messages/send
```

### List messages in an inbox

```bash
curl -s -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  https://api.agentmail.to/v0/inboxes/{inbox_id}/messages
```

### Reply to a message

```bash
curl -s -X POST -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Thanks for your email!"}' \
  https://api.agentmail.to/v0/inboxes/{inbox_id}/messages/{message_id}/reply
```

## OpenClaw Integration Notes

- The `AGENTMAIL_API_KEY` environment variable must be set in the OpenClaw environment.
- For security, never commit API keys to version control.
- Inbox IDs can be retrieved via the "List inboxes" endpoint.
- Use the existing inboxes (clawdia4me@agentmail.to etc.) for family communications.
- For programmatic email workflows, create new inboxes on-demand.

## Example Use Cases

Once AgentMail is integrated with OpenClaw, you can ask your agent to:

* "Create a new email inbox for my project"
* "Check my inbox for new emails"
* "Send an email to john@example.com about the meeting tomorrow"
* "Reply to the latest email from Sarah"
* "Forward the invoice email to accounting@company.com"