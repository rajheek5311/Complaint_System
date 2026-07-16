# AI-Based Complaint Resolution and Ticket Management System

Full-stack ticketing system built with Flask + SQLite + Bootstrap.

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
python app.py
```

Then open: http://127.0.0.1:5000

## Default Admin Login
- Email: admin@gmail.com
- Password: admin123

(This account is created automatically the first time you run app.py)

## Roles
- **User** — raises complaints, tracks their own tickets, comments
- **Support Agent** — works on tickets assigned to them, updates status, replies
- **Admin** — sees all tickets + analytics, assigns tickets to agents, manages status

## AI Classification Logic
See `utils/ai_logic.py`. Keyword-based priority + category detection runs
automatically every time a complaint is submitted.

## Notes
- `database.db` is created automatically on first run (SQLite).
- `email_log.txt` is created automatically to log "sent" notification emails
  (see `utils/email_utils.py` — this is a dummy/simulated email sender).
- Full step-by-step setup and troubleshooting guide was provided in chat.
