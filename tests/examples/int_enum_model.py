from enum import IntEnum

from pydantic import BaseModel


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Task(BaseModel):
    name: str
    priority: Priority
