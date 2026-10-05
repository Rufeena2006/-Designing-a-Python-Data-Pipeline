import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.hospitality_pipeline import clean, transform  # noqa: E402

COLS = ["booking_id", "guest_name", "email", "country", "room_type", "check_in", "check_out",
        "adults", "children", "room_rate", "status", "booking_channel", "booking_date"]


def row(**kw):
    base = dict(booking_id="B1", guest_name=" john smith ", email="J@X.com", country="uk",
                room_type="dlx", check_in="2025-03-01", check_out="2025-03-04", adults="2",
                children="", room_rate="100", status="canceled", booking_channel="direct",
                booking_date="2025-02-01")
    base.update(kw)
    return base


def test_missing_column_raises():
    with pytest.raises(ValueError):
        clean.clean(pd.DataFrame([{"booking_id": "1"}]))


def test_cleaning_standardises_values():
    c, r = clean.clean(pd.DataFrame([row()], columns=COLS))
    assert len(c) == 1 and r.empty
    rec = c.iloc[0]
    assert rec.guest_name == "John Smith" and rec.email == "j@x.com"
    assert rec.room_type == "Deluxe" and rec.status == "Cancelled" and rec.children == 0


def test_duplicates_and_bad_dates_rejected():
    df = pd.DataFrame([row(), row(), row(booking_id="B2", check_out="2025-02-01")], columns=COLS)
    c, r = clean.clean(df)
    assert len(c) == 1
    assert "check_out not after check_in" in r.iloc[0].reject_reason


def test_features_and_revenue():
    c, _ = clean.clean(pd.DataFrame([row(status="confirmed")], columns=COLS))
    f = transform.add_features(c)
    assert f.nights.iloc[0] == 3 and f.booking_value.iloc[0] == 300
    assert f.realized_revenue.iloc[0] == 300 and f.lead_time_days.iloc[0] == 28
    cancelled = transform.add_features(clean.clean(pd.DataFrame([row()], columns=COLS))[0])
    assert cancelled.realized_revenue.iloc[0] == 0
