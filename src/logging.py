"""Logging configuration. Stdlib logging, configured once."""
from __future__ import annotations

import logging

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure root logging once and return the app logger."""
    global _CONFIGURED
    if not _CONFIGURED:
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        )
        _CONFIGURED = True
    return logging.getLogger("agentic_reviewer")
