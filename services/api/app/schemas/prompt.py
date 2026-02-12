from datetime import date, datetime

from pydantic import BaseModel


class PromptBase(BaseModel):
    text: str
    reveal_date: date


class PromptCreate(PromptBase):
    pass


class PromptRead(PromptBase):
    id: int
    created_at: datetime | None

    class Config:
        from_attributes = True

