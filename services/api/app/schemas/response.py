from datetime import datetime

from pydantic import BaseModel


class ResponseCreate(BaseModel):
    text: str


class ResponseRead(BaseModel):
    id: int
    prompt_id: int
    text: str
    created_at: datetime | None

    class Config:
        from_attributes = True


class SimilarItem(BaseModel):
    id: int
    text: str
    score: float
