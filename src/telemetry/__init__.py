from fastapi import FastAPI

from ..config import Settings
from . import logging

__all__ = ["initialize_telemetry", "logging"]

from ..db import get_engine


def initialize_telemetry(
    app: FastAPI,
    settings: Settings,
) -> None:
    logging.initialize_logging(level=settings.log_level_int)
