from pydantic import BaseModel


class Node(BaseModel):
    value: int
    children: list["Node"] = []
