"""Stage 3 - Feature engineering and KPI aggregation."""
import pandas as pd

from .logger import get_logger

log = get_logger()


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["nights"] = (df["check_out"] - df["check_in"]).dt.days
    df["total_guests"] = df["adults"] + df["children"]
    df["booking_value"] = df["nights"] * df["room_rate"]
    df["is_cancelled"] = df["status"].isin(["Cancelled", "No-Show"])
    df["realized_revenue"] = df["booking_value"].where(~df["is_cancelled"], 0.0)
    df["lead_time_days"] = (df["check_in"] - df["booking_date"]).dt.days.clip(lower=0)
    df["stay_month"] = df["check_in"].dt.to_period("M").astype(str)
    df["stay_year"] = df["check_in"].dt.year
    return df


def monthly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("stay_month").agg(
        bookings=("booking_id", "count"),
        cancelled=("is_cancelled", "sum"),
        room_nights=("nights", "sum"),
        revenue=("realized_revenue", "sum"),
        avg_lead_time=("lead_time_days", "mean"),
    ).reset_index()
    sold = df[~df["is_cancelled"]].groupby("stay_month")["nights"].sum()
    out["adr"] = (out["revenue"] / out["stay_month"].map(sold)).round(2)
    out["cancellation_rate_pct"] = (out["cancelled"] / out["bookings"] * 100).round(1)
    out["revenue"] = out["revenue"].round(2)
    out["avg_lead_time"] = out["avg_lead_time"].round(1)
    return out


def channel_kpis(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("booking_channel").agg(
        bookings=("booking_id", "count"),
        revenue=("realized_revenue", "sum"),
        cancellation_rate_pct=("is_cancelled", lambda s: round(s.mean() * 100, 1)),
    ).reset_index()
    out["revenue"] = out["revenue"].round(2)
    return out.sort_values("revenue", ascending=False)


def room_type_kpis(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("room_type").agg(
        bookings=("booking_id", "count"),
        avg_rate=("room_rate", "mean"),
        revenue=("realized_revenue", "sum"),
    ).reset_index()
    out[["avg_rate", "revenue"]] = out[["avg_rate", "revenue"]].round(2)
    return out.sort_values("revenue", ascending=False)
