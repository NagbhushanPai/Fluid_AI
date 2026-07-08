from pydantic import BaseModel, Field


class RequestInput(BaseModel):
    request: str = Field(min_length=3)

