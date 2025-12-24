"""
Logging configuration for WEB-MON.
"""
import logging
import sys
from typing import Optional
from pathlib import Path

from config.settings import settings


def setup_logger(
    name: str = "webmon",
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure the application logger.

    Args:
        name: Logger name (default: "webmon")
        level: Logging level (default: from settings)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set logging level
    if level is None:
        level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        fmt=settings.logging.format,
        datefmt=settings.logging.date_format
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified or from settings)
    log_file = log_file or settings.logging.file
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Log to console if file logging fails
            logger.warning(f"Failed to set up file logging: {e}")

    return logger


def get_logger(name: str = "webmon") -> logging.Logger:
    """
    Get a logger instance. Creates it if it doesn't exist.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
