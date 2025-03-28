from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from src import config
from src.db import get_session, init_db

test_database_uri = "sqlite+aiosqlite://"  # In-memory sqlite database

# This import is necessary to ensure that the FastAPI app is properly configured!
# noqa makes sure this import is not reordered when formatting
from src.main import app  # noqa


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def test_db_engine() -> AsyncEngine:
    engine = create_async_engine(
        test_database_uri, echo=True, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    await init_db(engine)
    return engine


@pytest.fixture
async def test_db_session(test_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async_session = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def test_settings() -> config.Settings:
    settings = config.Settings(_env_file=None)
    settings.app_description = "Test description"
    settings.version = "1.2.3"
    return settings


@pytest.fixture
async def test_client(test_settings: config.Settings, test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_session] = lambda: test_db_session
    app.dependency_overrides[config.settings] = lambda: test_settings
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        yield client
    app.dependency_overrides.clear()
