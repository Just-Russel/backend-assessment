from uuid import UUID

import aiosqlite

from src.model.author import Author
from src.persistence.base import BaseRepository


class AuthorRepository(BaseRepository[Author]):
    async def initialize(self, conn: aiosqlite.Connection) -> None:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                uuid TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            )
        """)
        await conn.commit()

    async def create(self, author: Author, conn: aiosqlite.Connection) -> None:
        await conn.execute(
            "INSERT INTO authors (uuid, first_name, last_name) VALUES (?, ?, ?)",
            (str(author.uuid), author.first_name, author.last_name),
        )
        await conn.commit()

    async def get(self, author_uuid: UUID, conn: aiosqlite.Connection) -> Author | None:
        async with conn.execute(
            "SELECT uuid, first_name, last_name FROM authors WHERE uuid = ?", (str(author_uuid),)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return Author(uuid=UUID(row[0]), first_name=row[1], last_name=row[2])
        return None

    async def get_all(self, conn: aiosqlite.Connection) -> list[Author]:
        async with conn.execute("SELECT uuid, first_name, last_name FROM authors") as cursor:
            rows = await cursor.fetchall()
            return [Author(uuid=UUID(row[0]), first_name=row[1], last_name=row[2]) for row in rows]

    async def delete(self, author_uuid: UUID, conn: aiosqlite.Connection) -> None:
        await conn.execute("DELETE FROM authors WHERE uuid = ?", (str(author_uuid),))
        await conn.commit()
