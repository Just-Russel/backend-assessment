from uuid import UUID

from pydantic import BaseModel

from ..auth import UserRole


class AboutResponse(BaseModel):
    name: str
    description: str
    version: str


class HealthResponse(BaseModel):
    status: str = "OK"


class WhoAmIResponse(BaseModel):
    user_id: UUID
    email: str
    firebase_uid: str
    roles: list[UserRole]
