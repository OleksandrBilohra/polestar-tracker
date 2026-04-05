# Polestar Base

A focused Flask MVP for Volvo Polestar owners to save, browse, and filter real problems.

## What this does
- lets users add problems through the website
- saves them into SQLite
- filters by model, engine, year, and severity
- validates real model/engine/year combinations used in this project

## Stack
- Python 3.11+
- Flask
- Flask-SQLAlchemy
- SQLite
- Jinja templates
- vanilla CSS + JS

## Supported data in this MVP
### Models
- S60 Polestar
- V60 Polestar

### Engines
- 3.0 T6
- 2.0 T6 Drive-E

### Years
- 2014
- 2015
- 2016
- 2017
- 2018

Validation used in the app:
- 3.0 T6 -> 2014, 2015, 2016
- 2.0 T6 Drive-E -> 2016, 2017, 2018

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`

## Database
Data is saved in SQLite:
- file name: `polestar_tracker.db`
- location: Flask instance path for the app




