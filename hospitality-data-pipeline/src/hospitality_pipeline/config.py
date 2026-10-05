"""Central configuration. Override any value with an environment variable."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = Path(os.getenv("PIPELINE_RAW_DIR", BASE_DIR / "data" / "raw"))
PROCESSED_DIR = Path(os.getenv("PIPELINE_PROCESSED_DIR", BASE_DIR / "data" / "processed"))
LOG_DIR = Path(os.getenv("PIPELINE_LOG_DIR", BASE_DIR / "logs"))

# SQLite works out of the box. For MySQL use e.g.
# mysql+pymysql://user:password@localhost:3306/hospitality
DB_URL = os.getenv("PIPELINE_DB_URL", f"sqlite:///{BASE_DIR / 'data' / 'hospitality.db'}")

# Optional REST source (leave empty to skip API ingestion)
API_URL = os.getenv("BOOKINGS_API_URL", "")
API_TIMEOUT = int(os.getenv("BOOKINGS_API_TIMEOUT", "15"))

MAX_RETRIES = int(os.getenv("PIPELINE_MAX_RETRIES", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("PIPELINE_RETRY_BACKOFF", "2"))
SCHEDULE_TIME = os.getenv("PIPELINE_SCHEDULE_TIME", "02:00")

REQUIRED_COLUMNS = [
    "booking_id", "guest_name", "email", "country", "room_type",
    "check_in", "check_out", "adults", "children", "room_rate",
    "status", "booking_channel", "booking_date",
]

ROOM_TYPE_MAP = {
    "std": "Standard", "standard": "Standard", "standard room": "Standard",
    "dlx": "Deluxe", "deluxe": "Deluxe", "deluxe room": "Deluxe",
    "suite": "Suite", "ste": "Suite", "executive suite": "Suite",
    "family": "Family", "family room": "Family",
}
STATUS_MAP = {
    "confirmed": "Confirmed", "conf": "Confirmed",
    "cancelled": "Cancelled", "canceled": "Cancelled", "cancel": "Cancelled",
    "checked-out": "Completed", "checked out": "Completed", "completed": "Completed",
    "no-show": "No-Show", "no show": "No-Show", "noshow": "No-Show",
}

CHANNEL_MAP = {
    "direct": "Direct", "booking.com": "Booking.com", "expedia": "Expedia",
    "agoda": "Agoda", "walk-in": "Walk-in", "corporate": "Corporate",
}
