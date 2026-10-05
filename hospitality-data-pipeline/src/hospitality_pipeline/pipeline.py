"""Pipeline orchestrator: ingest -> clean -> transform -> load."""
import time
import traceback
from datetime import datetime

import pandas as pd

from . import clean as clean_mod
from . import ingest, load, transform
from .logger import get_logger

log = get_logger()


def run_pipeline(db_url: str = None) -> dict:
    run = {"run_started": datetime.now().isoformat(timespec="seconds"), "status": "FAILED",
           "rows_ingested": 0, "rows_clean": 0, "rows_rejected": 0, "duration_sec": 0.0,
           "error": ""}
    t0 = time.time()
    log.info("=== Pipeline run started ===")
    try:
        raw = ingest.ingest_all()                                   # Stage 1
        run["rows_ingested"] = len(raw)

        cleaned, rejected = clean_mod.clean(raw)                    # Stage 2
        run["rows_clean"], run["rows_rejected"] = len(cleaned), len(rejected)
        if cleaned.empty:
            raise RuntimeError("No valid rows left after cleaning")

        fact = transform.add_features(cleaned)                      # Stage 3
        tables = {
            "fact_bookings": fact,
            "kpi_monthly": transform.monthly_kpis(fact),
            "kpi_channel": transform.channel_kpis(fact),
            "kpi_room_type": transform.room_type_kpis(fact),
        }

        for name, df in tables.items():                             # Stage 4
            load.save_csv(df, name)
        if not rejected.empty:
            load.save_csv(rejected, "rejected_records")
        run["status"] = "SUCCESS"
        run["duration_sec"] = round(time.time() - t0, 2)
        tables["pipeline_runs"] = pd.DataFrame([run])
        load.save_sql(tables, db_url)
    except Exception as exc:
        run["status"] = "FAILED"
        run["error"] = f"{type(exc).__name__}: {exc}"
        run["duration_sec"] = round(time.time() - t0, 2)
        log.error("Pipeline failed: %s\n%s", exc, traceback.format_exc())
    else:
        log.info("=== Pipeline finished OK in %.2fs ===", run["duration_sec"])
    return run
