from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Post(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    author_uuid: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    title: str
    content: str


class Reply(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    author_uuid: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    post_uuid: UUID
    reply_uuid: UUID | None

    content: str
