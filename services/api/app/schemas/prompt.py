from datetime import datetime

from pydantic import BaseModel


class PromptCreate(BaseModel):
    text: str


class PromptRead(BaseModel):
    id: int
    text: str
    created_at: datetime | str | None = None
