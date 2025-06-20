from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Author(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
