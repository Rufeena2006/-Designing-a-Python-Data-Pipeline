"""Small retry decorator with exponential backoff."""
import functools
import time

from . import config
from .logger import get_logger

log = get_logger()


def retry(exceptions=(Exception,), attempts=None, backoff=None):
    attempts = attempts or config.MAX_RETRIES
    backoff = backoff if backoff is not None else config.RETRY_BACKOFF_SECONDS

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == attempts:
                        log.error("%s failed after %d attempts: %s", func.__name__, attempts, exc)
                        raise
                    wait = backoff * (2 ** (attempt - 1))
                    log.warning("%s attempt %d/%d failed (%s). Retrying in %.1fs",
                                func.__name__, attempt, attempts, exc, wait)
                    time.sleep(wait)
        return wrapper
    return decorator
