"""
logger.py
─────────
Structured logging with different formats for dev and production.

Development: Human-readable colored output
Production:  JSON lines — easy to parse with tools like jq or ship to Datadog
"""

from __future__ import annotations

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Outputs each log line as a JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "time":    datetime.utcnow().isoformat() + "Z",
            "level":   record.levelname,
            "module":  record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


class PrettyFormatter(logging.Formatter):
    """Colored, human-readable output for development."""

    COLORS = {
        "DEBUG":    "\033[36m",    # Cyan
        "INFO":     "\033[32m",    # Green
        "WARNING":  "\033[33m",    # Yellow
        "ERROR":    "\033[31m",    # Red
        "CRITICAL": "\033[35m",    # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        ts    = datetime.now().strftime("%H:%M:%S")
        return (
            f"{color}[{ts}] {record.levelname:<8}{self.RESET} "
            f"\033[90m{record.module}:\033[0m {record.getMessage()}"
        )


def setup_logging(
        *,
        env: str = "development",
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        format_type: str = "pretty",
    ) -> None:
    """
    Initialize structured logging system.

    Args:
        env: application environment (development/production)
        log_level: logging level string
        log_dir: directory for file logs
        format_type: "pretty" or "json"
    """

    # Convert level safely
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    # ── Console Handler ─────────────────────
    console = logging.StreamHandler()
    console.setLevel(level)

    if format_type == "json" or env == "production":
        console.setFormatter(JsonFormatter())
    else:
        console.setFormatter(PrettyFormatter())

    root.addHandler(console)

    # ── File Handler (optional) ─────────────
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        log_file = Path(log_dir) / f"app_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JsonFormatter())

        root.addHandler(file_handler)

    # ── Silence noisy libraries ─────────────
    for noisy in ["httpx", "urllib3", "chromadb", "sentence_transformers"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)


# Logger Factory
def get_logger(name: str) -> logging.Logger:
    """Return named logger."""
    return logging.getLogger(name)