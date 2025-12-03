from uuid import UUID

from pydantic import BaseModel


class Entity(BaseModel):
    id: UUID
    name: str
