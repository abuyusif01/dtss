# DTSS — Digital Twin Security Solution

A security testbed for industrial control systems: a simulated water-treatment plant running in Mininet, instrumented with ML-based intrusion detection, an event log, and email alerting.

The point is to have a network you can attack safely and a detector you can measure, without touching real PLC hardware.

## How it works

```
   sensor telemetry                classification                 response
 ┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
 │  Mininet twin    │          │      ML API      │          │   server_api     │
 │  plc1/2/3        │ ───────► │  Flask + sklearn │ ───────► │  MySQL + SMTP    │
 │  physical sim    │          │  5 models        │          │  email alerts    │
 │  attacker host   │          └──────────────────┘          └──────────────────┘
 └──────────────────┘                    │                            │
                                         ▼                            ▼
                                  ┌──────────────────────────────────────┐
                                  │  dashboard (Node) — event timeline    │
                                  └──────────────────────────────────────┘
```

Sensor readings from the twin are posted to the model server. If a reading is classified as an attack, the event is written to the database with a hash-based id and an alert is sent. The dashboard renders the timeline.

## Components

| Path | What it is |
|---|---|
| `dt/swat/` | Mininet topology for the SWaT-style plant: 3 PLCs, switch, attacker host, physical process simulation |
| `dt/fp/` | Second process topology and supporting scripts |
| `ML_API/` | Flask service serving 5 trained models. `train.ipynb` trains them, `label.py` generates attack labels from sensor thresholds |
| `server_api/` | Flask service for alerting: MySQL event writes, SMTP email, templates |
| `dashboard/` | Node front end. Event log keyed by SHA-256 hash of event content |
| `containers/` | Container definitions for the services |
| `libs/minicps/` | Mininet/ICS helper library |
| `report/` | Technical report (design, methodology, evaluation) |

## Models

Five classifiers are trained on labelled sensor data: random forest, gradient boosting, logistic regression, naive Bayes, and a stacking ensemble.

Random forest is the default — fastest inference, and the accuracy gap to the others is small. Stacking is the highest-accuracy option when latency does not matter. Selection happens per request via the `model_name` parameter.

## API

**ML API** (`ML_API/app.py`)

```
GET /get_status
    tank_liquidlevel, flowlevel, bottle_liquidlevel,
    motor_status, model_name (default: rf)
    → classification for the current plant state

GET /plc_log?file=<path>
    → contents of a PLC log file as JSON
```

**Alerting API** (`server_api/app.py`)

```
POST /send_mail
    → records the event and sends an alert
```

## Running it

Requirements: Linux (Mininet needs it), Python 3.10, Docker for the services.

```bash
git clone https://github.com/abuyusif01/dtss
cd dtss

# 1. model server
cd ML_API
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py

# 2. bring up the twin (separate terminal, needs sudo for Mininet)
cd dt/swat
sudo python3 run.py

# 3. alerting service needs its environment first
cd server_api
cat > .env <<'ENV'
EMAIL_ADDRESS=you@example.com
EMAIL_PASSWORD=app-password
EMAIL_PORT=587
EMAIL_INTERVAL=60
API_PORT=5001
ENV
python app.py

# 4. dashboard
cd dashboard
npm install && npm start
```

## Known limitations

- **Academic prototype.** Built for a research project, not production. The twin is a reduced SWaT model, not the full plant.
- **Credentials.** SMTP settings come from `.env`, but the MySQL host, user and password are still hardcoded in `server_api/app.py`. Move those to the environment before running this anywhere shared.
- **Detection scope.** The models classify sensor-level anomalies. They do not detect network-layer attacks directly; the attacker host in the topology is there to generate test traffic.
- **Dataset.** Training data derives from SWaT sensor behaviour. Results do not transfer to other plants without retraining.

## Report

`report/Technical Report - ID 903R.pdf` covers the design, threat model, training methodology and evaluation. Start there if you want the reasoning behind the architecture rather than the code.
