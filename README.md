# Hospitality Analytics Data Pipeline (Python)

An end-to-end, automated data pipeline for hotel / hospitality analytics. It ingests raw booking data from CSV files and an optional REST API, validates and cleans it with **pandas**, engineers revenue and operational features (nights stayed, realised revenue, lead time, ADR, cancellation rate), and stores analysis-ready tables in a **SQL database** (SQLite by default, MySQL supported) and timestamped **CSV** files.

![Architecture](docs/pipeline_architecture.png)

## What it does

| Stage | Module | Responsibility |
|---|---|---|
| 1. Ingestion | `ingest.py` | Reads all CSVs in `data/raw/`; pulls JSON from an API with `requests` (timeouts + retries) |
| 2. Cleaning | `clean.py` | Schema check, trimming, standardising room types / statuses / channels, date and number parsing, de-duplication, imputation, business-rule validation; invalid rows go to a reject file with a reason |
| 3. Transformation | `transform.py` | Adds `nights`, `booking_value`, `realized_revenue`, `lead_time_days`; builds monthly, channel and room-type KPI tables |
| 4. Storage | `load.py` | Writes tables to SQL in one transaction (idempotent full refresh) and to timestamped CSVs |
| Orchestration | `pipeline.py` | Runs the stages in order, records a run-audit row (status, counts, duration, error) |
| Automation | `scheduler.py` | Daily scheduled run (or use cron / Task Scheduler / Airflow) |

Cross-cutting: rotating-file logging (`logs/pipeline.log`), retry with exponential backoff, config via environment variables.

## Quick start

```bash
git clone <your-repo-url> && cd hospitality-data-pipeline
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python generate_sample_data.py 500    # creates a deliberately messy sample CSV
python main.py                        # run the pipeline once
python -m pytest -q                   # run unit tests
python scheduler.py                   # optional: run daily at 02:00
```

Outputs: `data/hospitality.db` (tables `fact_bookings`, `kpi_monthly`, `kpi_channel`, `kpi_room_type`, `pipeline_runs`), `data/processed/*.csv`, `logs/pipeline.log`.

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `PIPELINE_DB_URL` | local SQLite file | e.g. `mysql+pymysql://user:pass@localhost:3306/hospitality` (also `pip install pymysql`) |
| `BOOKINGS_API_URL` | empty (skip) | JSON endpoint returning a list of booking objects |
| `PIPELINE_SCHEDULE_TIME` | `02:00` | Daily run time for `scheduler.py` |
| `PIPELINE_MAX_RETRIES` | `3` | Retry attempts for API / DB operations |

## Expected input columns

`booking_id, guest_name, email, country, room_type, check_in, check_out, adults, children, room_rate, status, booking_channel, booking_date`

## Sample run (500 generated rows + 5% duplicates)

525 ingested -> 25 duplicates removed -> 20 rejected (invalid dates) -> 480 clean rows loaded.

## Project structure

```
hospitality-data-pipeline/
├── main.py                  # run once
├── scheduler.py             # daily automation
├── generate_sample_data.py  # messy test data
├── requirements.txt
├── src/hospitality_pipeline/
│   ├── config.py  logger.py  retry.py
│   ├── ingest.py  clean.py  transform.py  load.py  pipeline.py
├── tests/test_pipeline.py
├── docs/                    # diagram + design document
└── data/{raw,processed}/
```

## Extending

Add a new source by writing another `ingest_*` function that returns a DataFrame with the required columns; add a KPI by adding a function in `transform.py` and registering it in `pipeline.py`.
