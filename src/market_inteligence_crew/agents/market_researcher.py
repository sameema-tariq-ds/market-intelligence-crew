"""
Centralised logging setup.

Every module imports `get_logger(__name__)` — this means:
- All logs share one format.
- Log level is controlled by the LOG_LEVEL env variable.
- Logs go to BOTH the console (coloured via rich) AND a rotating file.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Args:
        name: Typically __name__ from the calling module.

    Returns:
        A logging.Logger instance.
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # ── Console handler ──────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ── File handler (rotating, max 5 MB, keep 3 backups) ────────────────
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        logs_dir / "market_intel.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # File always captures everything
    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger