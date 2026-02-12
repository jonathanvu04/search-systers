import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..models import Response
from ..schemas.response import SimilarItem

router = APIRouter(prefix="/responses", tags=["responses"])


@router.get("/", response_model=list)
def list_responses(db: Session = Depends(get_db)):
    """List all responses (useful for inspecting IDs)."""
    responses = db.query(Response).order_by(Response.id).all()
    return [{"id": r.id, "prompt_id": r.prompt_id, "text": r.text[:50]} for r in responses]


@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(response_id: int, db: Session = Depends(get_db)):
    """Delete a response by ID."""
    r = db.query(Response).filter(Response.id == response_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response {response_id} not found",
        )
    db.delete(r)
    db.commit()
    return None


@router.get("/{response_id}/similar", response_model=list[SimilarItem])
def get_similar_responses(
    response_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db),
):
    """
    Get top-k responses similar to the given response (same prompt, excluding self).
    Requires embeddings to be computed for responses; returns 501 if ranking
    is not yet implemented.
    """
    current = db.query(Response).filter(Response.id == response_id).first()
    if not current:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response {response_id} not found",
        )
    if not current.embedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response has no embedding; compute embeddings first",
        )

    others = (
        db.query(Response)
        .filter(
            Response.prompt_id == current.prompt_id,
            Response.id != response_id,
            Response.embedding.isnot(None),
        )
        .all()
    )

    others_data = [
        (r.id, json.loads(r.embedding))
        for r in others
    ]

    try:
        from services.ranking.rank import get_top_k_similar

        scored = get_top_k_similar(
            current_embedding=json.loads(current.embedding),
            current_response_id=response_id,
            others=others_data,
            top_k=top_k,
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Ranking not yet implemented by teammate",
        )

    # Map response_ids back to full response rows
    id_to_response = {r.id: r for r in others}
    result = []
    for rid, score in scored:
        if rid in id_to_response:
            result.append(
                SimilarItem(
                    id=rid,
                    text=id_to_response[rid].text,
                    score=score,
                )
            )
    return result
