from uuid import uuid4

import aiosqlite
import pytest

from src.model.author import Author
from src.persistence.author import AuthorRepository


@pytest.mark.asyncio
async def test_create_and_get_author() -> None:
    async with aiosqlite.connect(":memory:") as conn:
        repo = AuthorRepository()
        await repo.initialize(conn)

        author = Author(uuid=uuid4(), first_name="John", last_name="Doe")

        await repo.create(author, conn)

        fetched = await repo.get(author.uuid, conn)
        assert fetched is not None
        assert fetched.uuid == author.uuid
        assert fetched.first_name == "John"
        assert fetched.last_name == "Doe"


@pytest.mark.asyncio
async def test_get_all_authors() -> None:
    async with aiosqlite.connect(":memory:") as conn:
        repo = AuthorRepository()
        await repo.initialize(conn)

        author1 = Author(uuid=uuid4(), first_name="Alice", last_name="Smith")
        author2 = Author(uuid=uuid4(), first_name="Bob", last_name="Jones")

        await repo.create(author1, conn)
        await repo.create(author2, conn)

        authors = await repo.get_all(conn)
        assert len(authors) == 2
        uuids = {a.uuid for a in authors}
        assert author1.uuid in uuids
        assert author2.uuid in uuids


@pytest.mark.asyncio
async def test_delete_author() -> None:
    async with aiosqlite.connect(":memory:") as conn:
        repo = AuthorRepository()
        await repo.initialize(conn)

        author = Author(uuid=uuid4(), first_name="John", last_name="Doe")

        await repo.create(author, conn)

        fetched = await repo.get(author.uuid, conn)
        assert fetched is not None

        await repo.delete(author.uuid, conn)

        fetched = await repo.get(author.uuid, conn)
        assert fetched is None
