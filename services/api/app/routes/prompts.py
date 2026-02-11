from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..models import Prompt
from ..schemas.prompt import PromptCreate, PromptRead

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_prompts(db: Session = Depends(get_db)):
    """
    One-off helper endpoint to insert a few example prompts.
    In a real app you might replace this with a script or admin UI.
    """
    if db.query(Prompt).first():
        # Already seeded; no-op.
        return {"detail": "Prompts already seeded"}

    today = date.today()

    examples = [
        Prompt(
            text="What is your why?",
            reveal_date=today,
        ),
    ]

    db.add_all(examples)
    db.commit()

    return {"detail": f"Seeded {len(examples)} prompts"}


@router.post("/", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
def create_prompt(payload: PromptCreate, db: Session = Depends(get_db)):
    """
    Create a new prompt with a specific reveal_date.

    If a prompt already exists with the same text and reveal_date,
    return that existing prompt instead of inserting a duplicate.
    """
    existing = (
        db.query(Prompt)
        .filter(
            Prompt.text == payload.text,
            Prompt.reveal_date == payload.reveal_date,
        )
        .first()
    )
    if existing:
        return existing

    prompt = Prompt(
        text=payload.text,
        reveal_date=payload.reveal_date,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    return prompt


@router.get("/", response_model=list[PromptRead])
def list_prompts(db: Session = Depends(get_db)):
    """
    List all prompts, ordered by reveal_date then id.

    This is the easiest way to see existing prompt IDs while testing.
    """
    prompts = (
        db.query(Prompt)
        .order_by(Prompt.reveal_date.asc(), Prompt.id.asc())
        .all()
    )
    return prompts


@router.get("/today", response_model=PromptRead)
def get_todays_prompt(db: Session = Depends(get_db)):
    """
    Fetch the prompt scheduled for today's date.
    """
    today = date.today()

    prompt = (
        db.query(Prompt)
        .filter(Prompt.reveal_date == today)
        .order_by(Prompt.id.asc())
        .first()
    )

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prompt scheduled for today",
        )
    return prompt


@router.get("/{prompt_id}", response_model=PromptRead)
def get_prompt_by_id(prompt_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single prompt by its numeric ID.
    Useful while testing/inspecting specific prompts.
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with id {prompt_id} not found",
        )

    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """
    Delete a prompt by its ID.
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with id {prompt_id} not found",
        )

    db.delete(prompt)
    db.commit()

    # 204 No Content: empty response body
    return None

