"""Console + rotating-file logging."""
import logging
from logging.handlers import RotatingFileHandler

from . import config


def get_logger(name: str = "hospitality_pipeline") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # already configured
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    fileh = RotatingFileHandler(config.LOG_DIR / "pipeline.log",
                                maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    fileh.setFormatter(fmt)
    logger.addHandler(fileh)
    return logger
