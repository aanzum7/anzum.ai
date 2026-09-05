# ──────────────────────────────────────────────────────────────────────────────
# file: services/logger.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import logging
import os
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a structured logger.
    Defaults to ERROR level for a completely silent, clean terminal.
    """
    logger = logging.getLogger(name if name else __name__)
    if not logger.handlers:
        log_level_str = os.environ.get("LOG_LEVEL", "ERROR").upper()
        level = getattr(logging, log_level_str, logging.ERROR)
        logger.setLevel(level)

        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.propagate = False

        # Silence verbose third-party loggers
        for noisy in ("google", "google.generativeai", "google.api_core", "urllib3", "grpc"):
            logging.getLogger(noisy).setLevel(logging.ERROR)

    return logger
