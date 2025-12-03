from pydantic import BaseModel


class ListModel(BaseModel):
    tags: list[str]
    scores: list[int]
    active: bool
    description: str | None = None
