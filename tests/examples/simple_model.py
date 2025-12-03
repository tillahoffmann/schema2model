from pydantic import BaseModel


class SimpleModel(BaseModel):
    a: int
    b: float
    c: str
