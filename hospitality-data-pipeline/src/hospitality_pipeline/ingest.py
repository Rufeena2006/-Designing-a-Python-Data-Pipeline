"""Stage 1 - Data ingestion (CSV files and optional REST API)."""
from pathlib import Path

import pandas as pd
import requests

from . import config
from .logger import get_logger
from .retry import retry

log = get_logger()


def ingest_csv(directory: Path = None) -> pd.DataFrame:
    """Read every CSV in the raw directory and tag rows with their source file."""
    directory = Path(directory or config.RAW_DIR)
    frames = []
    for path in sorted(directory.glob("*.csv")):
        try:
            df = pd.read_csv(path, dtype=str)  # read as text; cleaning stage converts types
            df["source_file"] = path.name
            frames.append(df)
            log.info("Ingested %d rows from %s", len(df), path.name)
        except Exception as exc:  # one bad file must not stop the run
            log.error("Skipping unreadable file %s: %s", path.name, exc)
    if not frames:
        log.warning("No CSV files found in %s", directory)
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@retry(exceptions=(requests.RequestException,))
def _fetch(url: str) -> list:
    response = requests.get(url, timeout=config.API_TIMEOUT)
    response.raise_for_status()
    return response.json()


def ingest_api(url: str = None) -> pd.DataFrame:
    """Pull booking records (JSON list) from a REST endpoint."""
    url = url or config.API_URL
    if not url:
        return pd.DataFrame()
    records = _fetch(url)
    df = pd.DataFrame(records).astype("string")
    df["source_file"] = "api"
    log.info("Ingested %d rows from API %s", len(df), url)
    return df


def ingest_all() -> pd.DataFrame:
    frames = [f for f in (ingest_csv(), ingest_api()) if not f.empty]
    if not frames:
        raise RuntimeError("No data ingested from any source")
    combined = pd.concat(frames, ignore_index=True)
    log.info("Total raw rows ingested: %d", len(combined))
    return combined
