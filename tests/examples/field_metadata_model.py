from pydantic import BaseModel, Field


class FieldMetadataModel(BaseModel):
    with_description: str = Field(description="A field with a description")
    with_examples: str = Field(examples=["foo", "bar"])
    deprecated_field: str = Field(deprecated=True)
    multiple_of_field: int = Field(multiple_of=5)
