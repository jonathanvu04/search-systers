from fastapi import FastAPI

from .core.db import Base, engine
from .core.cors import *  # if you later configure CORS here
from .routes import prompts, responses

app = FastAPI(title="search-systers API")


@app.on_event("startup")
def on_startup() -> None:
    """
    Create database tables on startup.

    For larger projects you might use Alembic migrations instead,
    but for now this ensures our SQLite prompts table exists.
    """
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(prompts.router)
app.include_router(responses.router)