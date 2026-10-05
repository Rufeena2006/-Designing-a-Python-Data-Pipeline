"""Create a deliberately messy sample hotel-bookings CSV for testing.

Usage: python generate_sample_data.py [rows]
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
OUT = Path(__file__).parent / "data" / "raw" / "bookings_sample.csv"

ROOMS = {"Standard": 90, "Deluxe": 140, "Suite": 260, "Family": 180}
ROOM_VARIANTS = ["Standard", "STD", "standard room", "Deluxe", "dlx", "Suite", "executive suite", "Family", "family room"]
STATUSES = ["Confirmed", "confirmed", "Cancelled", "canceled", "Checked-Out", "No-Show", "Completed"]
CHANNELS = ["Direct", "Booking.com", "Expedia", "Agoda", "Walk-in", "corporate"]
COUNTRIES = ["india", "United States", "UK", "germany", "France", "uae", "Japan", "Australia"]
FIRST = ["Aarav", "Priya", "John", "Emma", "Liam", "Sara", "Rahul", "Mei", "Omar", "Anna"]
LAST = ["Sharma", "Smith", "Khan", "Brown", "Patel", "Garcia", "Lee", "Muller", "Rossi", "Singh"]

rows = []
for i in range(1, N + 1):
    room = random.choice(list(ROOMS))
    ci = date(2025, 1, 1) + timedelta(days=random.randint(0, 540))
    nights = random.randint(1, 9)
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    rows.append({
        "booking_id": f"BK{i:05d}",
        "guest_name": f"  {name.lower()} " if random.random() < 0.1 else name,
        "email": f"{name.lower().replace(' ', '.')}{i}@example.com",
        "country": random.choice(COUNTRIES),
        "room_type": random.choice([v for v in ROOM_VARIANTS if v.lower().startswith(room.lower()[:3]) or room == "Suite" and "suite" in v.lower()] or [room]),
        "check_in": ci.strftime("%Y-%m-%d") if random.random() > 0.15 else ci.strftime("%d/%m/%Y"),
        "check_out": (ci + timedelta(days=nights)).strftime("%Y-%m-%d"),
        "adults": random.randint(1, 4),
        "children": random.choice([0, 0, 0, 1, 2]),
        "room_rate": round(ROOMS[room] * random.uniform(0.8, 1.4), 2),
        "status": random.choice(STATUSES),
        "booking_channel": random.choice(CHANNELS),
        "booking_date": (ci - timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d"),
    })

df = pd.DataFrame(rows)
# inject realistic data-quality problems
df.loc[df.sample(frac=0.04, random_state=1).index, "room_rate"] = None       # missing rate
df.loc[df.sample(frac=0.03, random_state=2).index, "email"] = "not-an-email"  # bad email
df.loc[df.sample(frac=0.02, random_state=3).index, "check_out"] = "2000-01-01"  # check-out before check-in
df.loc[df.sample(frac=0.02, random_state=4).index, "check_in"] = "31-31-2025"  # unparseable date
df.loc[df.sample(frac=0.03, random_state=5).index, "children"] = None
df = pd.concat([df, df.sample(frac=0.05, random_state=6)], ignore_index=True)  # duplicates

OUT.parent.mkdir(parents=True, exist_ok=True)
df.sample(frac=1, random_state=7).to_csv(OUT, index=False)
print(f"Wrote {len(df)} messy rows to {OUT}")
