import asyncpg

from src.model.user import User


class UserRepository:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def initialize(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS users (
            uuid uuid PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL
        );
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)

    async def clear(self) -> None:
        query = "TRUNCATE TABLE users RESTART IDENTITY CASCADE;"
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)

    async def create(self, user: User) -> User:
        query = """
        INSERT INTO users (uuid, username, email, created_at)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user.uuid,
                user.username,
                user.email,
                user.created_at,
            )
            return User(**row)

    async def get(self, user_uuid: str):
        query = "SELECT * FROM users WHERE uuid = $1"
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, user_uuid)
            if row:
                return User(**row)

    async def update(self, user: User) -> User | None:
        query = """
        UPDATE users
        SET username = $1, email = $2, created_at = $3
        WHERE uuid = $4
        RETURNING *
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user.username,
                user.email,
                user.created_at,
                user.uuid,
            )
            if row:
                return User(**row)

    async def delete(self, user_uuid: str) -> None:
        query = "DELETE FROM users WHERE uuid = $1"
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, user_uuid)
