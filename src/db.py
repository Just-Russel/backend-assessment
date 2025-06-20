import aiosqlite

from src.persistence.author import AuthorRepository


async def init_db(db_uri: str) -> None:
    async with aiosqlite.connect(db_uri) as conn:
        await AuthorRepository().initialize(conn)
