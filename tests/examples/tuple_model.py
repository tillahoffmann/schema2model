from pydantic import BaseModel


class Coordinates(BaseModel):
    point: tuple[int, int]
    point_3d: tuple[float, float, float]
