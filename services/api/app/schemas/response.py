from datetime import datetime

from pydantic import BaseModel


class ResponseCreate(BaseModel):
    text: str


class ResponseSubmit(BaseModel):
    prompt_id: int
    text: str
    user_id: str | None = None


class ResponseSubmitResult(BaseModel):
    response_id: int
    detail: str = "Response saved with embedding"


class ResponseRead(BaseModel):
    id: int
    prompt_id: int
    text: str
    created_at: datetime | str | None = None


class SimilarItem(BaseModel):
    id: int
    text: str
    score: float
