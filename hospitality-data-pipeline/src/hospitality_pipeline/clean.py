"""Stage 2 - Validation and cleaning."""
import pandas as pd

from . import config
from .logger import get_logger

log = get_logger()
EMAIL_REGEX = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"


def parse_dates(series: pd.Series) -> pd.Series:
    """Parse ISO dates first (YYYY-MM-DD), then fall back to day-first formats (DD/MM/YYYY)."""
    iso = pd.to_datetime(series, errors="coerce", format="%Y-%m-%d")
    fallback = pd.to_datetime(series[iso.isna()], errors="coerce", format="mixed", dayfirst=True)
    return iso.fillna(fallback)


def validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in config.REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean(df: pd.DataFrame):
    """Return (clean_df, rejected_df). Rejected rows keep a 'reject_reason'."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    validate_schema(df)
    start_rows = len(df)

    # 1. Trim whitespace; treat empty strings as missing
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype("string").str.strip().replace({"": pd.NA})

    # 2. Standardise categorical text
    df["guest_name"] = df["guest_name"].str.title()
    df["email"] = df["email"].str.lower()
    df["country"] = df["country"].str.title()
    low = df["booking_channel"].str.lower()
    df["booking_channel"] = low.map(config.CHANNEL_MAP).fillna(df["booking_channel"].str.title())
    df["room_type"] = df["room_type"].str.lower().map(config.ROOM_TYPE_MAP)
    df["status"] = df["status"].str.lower().map(config.STATUS_MAP)

    # 3. Type conversion (bad values become NaT / NaN instead of crashing)
    for col in ("check_in", "check_out", "booking_date"):
        df[col] = parse_dates(df[col])
    for col in ("adults", "children", "room_rate"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Remove duplicate bookings (keep the last record received)
    df = df.drop_duplicates(subset="booking_id", keep="last")
    dupes_removed = start_rows - len(df)

    # 5. Fill gaps
    df["children"] = df["children"].fillna(0)
    df["country"] = df["country"].fillna("Unknown")
    df["booking_channel"] = df["booking_channel"].fillna("Unknown")
    df["status"] = df["status"].fillna("Confirmed")
    median_rate = df.groupby("room_type")["room_rate"].transform("median")
    df["room_rate"] = df["room_rate"].fillna(median_rate)

    # 6. Business-rule validation -> rejects
    reasons = pd.Series("", index=df.index, dtype="object")
    def flag(mask, text):
        reasons.loc[mask.fillna(True)] += text
    flag(df["booking_id"].isna(), "missing booking_id;")
    flag(df["room_type"].isna(), "unknown room_type;")
    flag(df["check_in"].isna() | df["check_out"].isna(), "invalid date;")
    flag(df["check_out"] <= df["check_in"], "check_out not after check_in;")
    flag(df["room_rate"].isna() | (df["room_rate"] <= 0), "invalid room_rate;")
    flag(df["adults"].isna() | (df["adults"] < 1), "invalid adults;")
    invalid_email = ~df["email"].fillna("").str.match(EMAIL_REGEX)
    df["email"] = df["email"].mask(invalid_email, pd.NA)  # blank bad emails, keep the row

    bad = reasons != ""
    rejected = df[bad].copy()
    rejected["reject_reason"] = reasons[bad]
    cleaned = df[~bad].copy()
    cleaned["adults"] = cleaned["adults"].astype(int)
    cleaned["children"] = cleaned["children"].astype(int)

    log.info("Cleaning: %d in | %d duplicates removed | %d rejected | %d clean",
             start_rows, dupes_removed, len(rejected), len(cleaned))
    return cleaned.reset_index(drop=True), rejected.reset_index(drop=True)
