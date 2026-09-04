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
    Defaults to WARNING level for a completely clean terminal.
    """
    logger = logging.getLogger(name if name else __name__)
    if not logger.handlers:
        # Default to WARNING to eliminate terminal spam; override with LOG_LEVEL=INFO if debugging
        log_level_str = os.environ.get("LOG_LEVEL", "WARNING").upper()
        level = getattr(logging, log_level_str, logging.WARNING)
        logger.setLevel(level)

        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
