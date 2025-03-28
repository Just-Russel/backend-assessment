import logging

import pytest

from src.config import settings
from src.telemetry.logging import initialize_logging


@pytest.mark.parametrize("level", [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL])
def test_initialize_logging_valid_levels(level: int) -> None:
    initialize_logging(level)
    assert logging.getLogger().level == level


def test_initialize_logging_invalid_level() -> None:
    config_settings = settings()

    config_settings.log_level = "invalid"
    assert config_settings.log_level_int == logging.NOTSET

    initialize_logging(config_settings.log_level_int)
    assert logging.getLogger().level == config_settings.log_level_int
