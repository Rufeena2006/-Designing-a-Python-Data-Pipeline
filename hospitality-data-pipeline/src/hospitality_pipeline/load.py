"""Stage 4 - Storage (timestamped CSV + SQL database)."""
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine

from . import config
from .logger import get_logger
from .retry import retry

log = get_logger()


def save_csv(df: pd.DataFrame, name: str) -> str:
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = config.PROCESSED_DIR / f"{name}_{stamp}.csv"
    df.to_csv(path, index=False)
    df.to_csv(config.PROCESSED_DIR / f"{name}_latest.csv", index=False)
    log.info("Saved %d rows -> %s", len(df), path.name)
    return str(path)


@retry(exceptions=(Exception,))
def save_sql(tables: dict, db_url: str = None) -> None:
    """Full-refresh load: each run replaces the tables, so reruns are idempotent."""
    engine = create_engine(db_url or config.DB_URL)
    with engine.begin() as conn:  # one transaction: all tables load or none do
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)
            log.info("Loaded table '%s' (%d rows)", name, len(df))
    engine.dispose()
