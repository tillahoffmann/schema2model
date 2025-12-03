from typing import Literal

from pydantic import BaseModel


class Task(BaseModel):
    status: Literal["pending", "active", "done"]
    priority: Literal["low", "medium", "high"]
