"""
Logging setup: human-readable console + JSON-lines file.
All log lines carry a request_id for traceability.
"""

import logging
import sys
import json
import os
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        obj = {
            "ts":     datetime.now(timezone.utc).isoformat(),
            "level":  record.levelname,
            "logger": record.name,
            "msg":    record.getMessage(),
        }
        if record.exc_info:
            obj["exc"] = self.formatException(record.exc_info)
        return json.dumps(obj, ensure_ascii=False)


def setup_logger(name: str = "agent_system") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console — human-readable
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)-22s │ %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(ch)

    # File — JSON lines
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "agents.log")
    fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_JsonFormatter())
    logger.addHandler(fh)

    logger.propagate = False
    return logger


def get_logger(module: str) -> logging.Logger:
    """Return a child logger under the root agent_system logger."""
    setup_logger("agent_system")   # ensure root is configured
    return logging.getLogger(f"agent_system.{module}")
