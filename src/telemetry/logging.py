import logging
from typing import Any

from src.config import settings as config_settings


settings = config_settings()


def initialize_logging(level: int) -> None:
    logging.basicConfig(level=level, force=True)
