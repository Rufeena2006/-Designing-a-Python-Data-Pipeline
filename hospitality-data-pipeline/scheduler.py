"""Run the pipeline every day at PIPELINE_SCHEDULE_TIME:  python scheduler.py

Alternatives: cron  ->  0 2 * * * cd /path/to/project && python main.py
              Windows Task Scheduler, or an Airflow DAG calling run_pipeline().
"""
import time

import schedule

from src.hospitality_pipeline import config
from src.hospitality_pipeline.logger import get_logger
from src.hospitality_pipeline.pipeline import run_pipeline

log = get_logger()


def job():
    result = run_pipeline()
    if result["status"] != "SUCCESS":
        log.critical("Scheduled run failed: %s", result["error"])  # hook email/Slack alert here


if __name__ == "__main__":
    schedule.every().day.at(config.SCHEDULE_TIME).do(job)
    log.info("Scheduler started. Daily run at %s", config.SCHEDULE_TIME)
    while True:
        schedule.run_pending()
        time.sleep(30)
