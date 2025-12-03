from pydantic import BaseModel, Field


class Person(BaseModel):
    age: int = Field(gt=0, lt=150)
    name: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0.0, le=100.0)
