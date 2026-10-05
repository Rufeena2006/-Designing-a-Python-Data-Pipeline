import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(13, 6.2))
ax.set_xlim(0, 13); ax.set_ylim(0, 6.2); ax.axis("off")

def box(x, y, w, h, title, lines, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc=color, ec="#33415c", lw=1.4))
    ax.text(x + w/2, y + h - 0.28, title, ha="center", va="center", fontsize=10.5, weight="bold", color="#0b132b")
    ax.text(x + w/2, y + h/2 - 0.22, "\n".join(lines), ha="center", va="center", fontsize=8.3, color="#0b132b")

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16, lw=1.8, color="#1c2541"))

# sources
box(0.2, 3.9, 2.0, 1.3, "DATA SOURCES", ["PMS / booking CSVs", "Channel REST API"], "#e0e1dd")
box(0.2, 1.9, 2.0, 1.3, "Raw landing zone", ["data/raw/*.csv", "(never modified)"], "#e0e1dd")
# stages
box(2.9, 2.5, 2.1, 2.6, "1. INGESTION", ["pandas.read_csv", "requests.get + retry", "tag source_file", "combine all sources"], "#bde0fe")
box(5.4, 2.5, 2.1, 2.6, "2. CLEANING", ["schema check", "trim / standardise text", "parse dates, numbers", "dedupe booking_id", "impute missing rates", "business-rule checks"], "#a2d2ff")
box(7.9, 2.5, 2.1, 2.6, "3. TRANSFORM", ["nights, guests", "booking value", "realised revenue", "lead time", "KPI tables: ADR,", "cancellation rate"], "#cdb4db")
box(10.4, 3.4, 2.4, 1.7, "4. STORAGE", ["SQL (SQLite / MySQL)", "timestamped CSV"], "#b7e4c7")
box(10.4, 1.5, 2.4, 1.5, "Reject quarantine", ["rejected_records.csv", "with reject_reason"], "#ffd6a5")
for x1, x2 in [(2.2, 2.9), (5.0, 5.4), (7.5, 7.9), (10.0, 10.4)]:
    arrow(x1, 3.8, x2, 3.8)
arrow(1.2, 3.9, 1.2, 3.2)
arrow(6.45, 2.5, 10.4, 2.25)
ax.text(8.4, 2.1, "invalid rows", fontsize=8, style="italic", color="#7f4f24")
ax.text(11.6, 5.45, "Power BI / SQL\nanalysis", ha="center", fontsize=9, weight="bold", color="#1b4332")
arrow(11.6, 5.1, 11.6, 5.35)
# cross-cutting
ax.add_patch(FancyBboxPatch((2.9, 0.35), 9.9, 0.85, boxstyle="round,pad=0.04,rounding_size=0.1",
                            fc="#fefae0", ec="#bc6c25", lw=1.4, ls="--"))
ax.text(7.85, 0.78, "CROSS-CUTTING SERVICES\nOrchestrator (pipeline.py)  |  Rotating-file logging  |  Retry with backoff  |  Scheduler (schedule / cron)  |  Run audit table", ha="center", va="center", fontsize=7.4, color="#603808", weight="bold")
ax.text(6.5, 5.95, "Hospitality Analytics - Python Data Pipeline", ha="center", fontsize=14, weight="bold", color="#0b132b")
plt.savefig("docs/pipeline_architecture.png", dpi=170, bbox_inches="tight", facecolor="white")
