from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    username: str
    email: str
