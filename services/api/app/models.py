from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text

from .core.db import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    # Calendar date when the prompt should be revealed
    reveal_date = Column(Date, nullable=False, index=True)
    # Timestamp when the prompt row was created
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    # JSON array of floats from TF-IDF (or other) embedding; nullable until computed
    embedding = Column(Text, nullable=True)

