from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from .db import get_session, ping_db


@pytest.mark.anyio
async def test_get_session() -> None:
    """
    Test that the get_session function returns an AsyncSession object.
    """

    async for session in get_session():
        assert isinstance(session, AsyncSession)


@pytest.mark.anyio
async def test_ping_db() -> None:
    """
    Test that the ping_db function can connect to the database.
    """

    with mock.patch("src.db.get_engine") as mock_get_engine:
        await ping_db()
        mock_get_engine.assert_called_once()
        mock_get_engine().connect.assert_called_once()


@pytest.mark.anyio
async def test_ping_db_exception() -> None:
    """
    Test that the ping_db function raises a RuntimeError when it cannot connect to the database.
    """

    with mock.patch("src.db.get_engine") as mock_get_engine:
        mock_engine = mock.AsyncMock(AsyncEngine)
        mock_get_engine.return_value = mock_engine
        mock_engine.connect.side_effect = Exception("Test connection error")

        with pytest.raises(RuntimeError):
            await ping_db()
