"""Run the pipeline once:  python main.py"""
import sys

from src.hospitality_pipeline.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline()
    print("\nRun summary:", result)
    sys.exit(0 if result["status"] == "SUCCESS" else 1)
