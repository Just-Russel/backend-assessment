import asyncpg
import pytest_asyncio


@pytest_asyncio.fixture
async def db_pool():
    async with asyncpg.create_pool(
        user="postgres",
        password="postgres",
        database="postgres",
        host="localhost",
        port=5432,
    ) as pool:
        yield pool
