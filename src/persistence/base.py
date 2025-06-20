from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

import aiosqlite

T = TypeVar("T")


class BaseRepository[T](ABC):
    @abstractmethod
    async def initialize(self, conn: aiosqlite.Connection) -> None:
        pass

    @abstractmethod
    async def create(self, obj: T, conn: aiosqlite.Connection) -> None:
        pass

    @abstractmethod
    async def get(self, obj_uuid: UUID, conn: aiosqlite.Connection) -> T | None:
        pass

    @abstractmethod
    async def get_all(self, conn: aiosqlite.Connection) -> list[T]:
        pass

    @abstractmethod
    async def delete(self, obj_uuid: UUID, conn: aiosqlite.Connection) -> None:
        pass
