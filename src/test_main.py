from unittest import mock

import pytest

from .config import settings as get_settings
from .db import get_engine
from .main import app, lifespan, start_server


def test_start_server() -> None:
    """
    Test that the start_server function calls uvicorn.run with the expected parameters.
    """

    with mock.patch("src.main.uvicorn.run") as mock_uvicorn_run:
        start_server()

    expected_options = {
        "host": get_settings().host,
        "port": get_settings().port,
        "reload": get_settings().environment == "development" and get_settings().auto_reload,
        "log_level": get_settings().log_level_int,
    }

    mock_uvicorn_run.assert_called_once_with("src.main:app", **expected_options)


@pytest.mark.anyio
async def test_lifespan_initializes_db() -> None:
    """
    Test that the lifespan context manager initializes the database.
    """

    with mock.patch("src.main.init_db") as mock_init_db:
        async with lifespan(app):
            mock_init_db.assert_called_once_with(get_engine())
