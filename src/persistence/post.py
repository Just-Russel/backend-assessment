from uuid import UUID

import asyncpg

from src.model.post import Post, Reply


class PostRepository:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def initialize(self):
        query = """
        CREATE TABLE IF NOT EXISTS posts (
            uuid uuid PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            author_uuid uuid NOT NULL REFERENCES users(uuid)
        )
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)

    async def clear(self):
        query = "TRUNCATE TABLE posts RESTART IDENTITY CASCADE;"
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)

    async def create(self, post: Post) -> Post:
        query = """
        INSERT INTO posts (uuid, title, content, created_at, author_uuid)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchval(
                query,
                post.uuid,
                post.title,
                post.content,
                post.created_at,
                post.author_uuid,
            )
            return Post(**row)

    async def update(self, post: Post) -> Post | None:
        query = """
        UPDATE posts
        SET title = $1, content = $2, created_at = $3
        WHERE uuid = $4
        RETURNING *
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                post.title,
                post.content,
                post.created_at,
                post.uuid,
            )
            if row:
                return Post(**row)

    async def get(self, post_uuid: UUID) -> Post | None:
        query = "SELECT * FROM posts WHERE uuid = $1"
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, post_uuid)
            if row:
                return Post(**row)

    async def delete(self, post_uuid: UUID) -> None:
        query = "DELETE FROM posts WHERE uuid = $1"
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, post_uuid)


class ReplyRepository:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def initialize(self):
        query = """
        CREATE TABLE IF NOT EXISTS replies (
            uuid uuid PRIMARY KEY,
            post_uuid uuid NOT NULL REFERENCES posts(uuid) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            author_uuid uuid NOT NULL REFERENCES users(uuid)
        )
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)

    async def clear(self):
        query = "TRUNCATE TABLE replies RESTART IDENTITY CASCADE;"
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)

    async def create(self, reply: Reply) -> Reply:
        query = """
        INSERT INTO replies (uuid, post_uuid, content, created_at, author_uuid)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchval(
                query,
                reply.uuid,
                reply.post_uuid,
                reply.content,
                reply.created_at,
                reply.author_uuid,
            )
            return Reply(**row)

    async def get(self, reply_uuid: UUID) -> Reply | None:
        query = "SELECT * FROM replies WHERE uuid = $1"
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, reply_uuid)
            if row:
                return Reply(**row)

    async def get_for_post(self, post_uuid: int) -> list[Reply]:
        query = "SELECT * FROM replies WHERE post_uuid = $1"
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, post_uuid)
            return [Reply(**row) for row in rows]

    async def update(self, reply_id: int, content: str) -> Reply | None:
        query = """
        UPDATE replies
        SET content = $1
        WHERE uuid = $2
        RETURNING *
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchval(query, content, reply_id)
            if row:
                return Reply(**row)

    async def delete(self, reply_uuid: UUID) -> None:
        query = "DELETE FROM replies WHERE uuid = $1"
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, reply_uuid)
