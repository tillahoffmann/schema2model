from pydantic import AnyHttpUrl, BaseModel


class UrlModel(BaseModel):
    website: AnyHttpUrl
    name: str
