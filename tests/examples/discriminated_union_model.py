from typing import Literal

from pydantic import BaseModel, Field


class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int


class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float


class Owner(BaseModel):
    name: str
    pet: Cat | Dog = Field(discriminator="pet_type")
