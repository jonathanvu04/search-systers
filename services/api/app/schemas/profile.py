from datetime import datetime

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    name: str | None = None
    age: int | None = None


class ProfileRead(BaseModel):
    id: str
    name: str | None = None
    age: int | None = None
    created_at: datetime | str | None = None
