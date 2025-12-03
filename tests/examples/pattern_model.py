from pydantic import BaseModel, Field


class PatternModel(BaseModel):
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")
