# server_api

Flask service that records security events and sends email alerts.

## Setup

```
pip install flask flask-cors mysql-connector-python python-dotenv
cp .env.example .env     # fill in SMTP and MySQL values
python app.py
```

## Environment

All credentials come from `.env`:

| Variable | Purpose |
|---|---|
| `EMAIL_ADDRESS`, `EMAIL_PASSWORD` | SMTP account. Gmail requires an app password. |
| `EMAIL_PORT` | SMTP port, default 587 |
| `EMAIL_INTERVAL` | seconds between alert checks, default 60 |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL connection. Required — the service exits if user or password is missing. |
| `API_PORT` | listen port, default 5001 |
| `FLASK_DEBUG` | `true` enables the Flask debugger. Leave false. |

## Endpoint

`POST /send_mail` — body is JSON with the event payload and recipient. Writes the event, then sends the alert.
