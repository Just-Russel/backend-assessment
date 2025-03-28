from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import Session, SQLModel, create_engine  # noqa: F401
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings
from .model import *  # noqa: F401,F403 NOSONAR

app_settings = settings()

_engine: AsyncEngine = create_async_engine(app_settings.db_uri_async, echo=app_settings.echo_sql)


def get_engine() -> AsyncEngine:
    return _engine


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# get_session async version:
async def get_session() -> AsyncGenerator[AsyncSession]:
    engine = get_engine()
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


def get_sync_session() -> Session:
    return Session(create_engine(app_settings.db_uri_async, echo=app_settings.echo_sql))


async def ping_db() -> None:
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        raise RuntimeError(f"Database connection error: {e}") from e
