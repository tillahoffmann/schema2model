from pydantic import BaseModel


class TagContainer(BaseModel):
    tags: set[str]
    ids: set[int]
