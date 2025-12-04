import os
import logging
from logging.handlers import TimedRotatingFileHandler
from config import LOG_DIR

def setup_logger(name="webmon"):
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(
        f"{LOG_DIR}/{name}.log",
        when="D",
        interval=1,
        backupCount=30
    )
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger
