from pydantic import BaseModel


class BytesModel(BaseModel):
    data: bytes
    name: str
