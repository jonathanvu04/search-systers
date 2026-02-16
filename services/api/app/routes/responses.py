import json

from fastapi import APIRouter, HTTPException, status

from ..core.supabase import supabase
from ..schemas.response import SimilarItem

router = APIRouter(prefix="/responses", tags=["responses"])


def _supabase_check():
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )


@router.get("/")
def list_responses():
    """List all responses."""
    _supabase_check()
    r = supabase.table("responses").select("id, prompt_id, text").order("id").execute()
    data = r.data or []
    return [{"id": x["id"], "prompt_id": x["prompt_id"], "text": (x["text"] or "")[:50]} for x in data]


@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(response_id: int):
    """Delete a response by ID."""
    _supabase_check()
    r = supabase.table("responses").select("id").eq("id", response_id).limit(1).execute()
    if not r.data or len(r.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Response {response_id} not found")
    supabase.table("responses").delete().eq("id", response_id).execute()
    return None


@router.post("/{response_id}/embed", status_code=status.HTTP_200_OK)
def compute_embedding(response_id: int):
    """
    Compute embedding for a response and store in Supabase.
    Call this after the frontend inserts a response (Option A).
    """
    _supabase_check()
    r = supabase.table("responses").select("*").eq("id", response_id).limit(1).execute()
    if not r.data or len(r.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Response {response_id} not found")

    row = r.data[0]
    text = row.get("text")
    prompt_id = row.get("prompt_id")
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Response has no text")

    # Step 2: Load all responses for this prompt_id (including the new one)
    all_r = supabase.table("responses").select("id, text").eq("prompt_id", prompt_id).order("id").execute()
    rows = all_r.data or []
    if not rows:
        return {"detail": "No responses found for prompt", "response_id": response_id}

    corpus = [x["text"] or "" for x in rows]
    ids = [x["id"] for x in rows]

    try:
        from services.embedding.tfidf import embed_all

        # Steps 3–4: Fit TF-IDF on corpus, transform all, L2-normalize
        vectors = embed_all(corpus)
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Embedding not yet implemented by teammate",
        )

    # Update ALL embeddings so vocabulary/IDF stay consistent
    for rid, vec in zip(ids, vectors):
        supabase.table("responses").update({"embedding": json.dumps([float(x) for x in vec])}).eq("id", rid).execute()

    return {"detail": "Embeddings computed and stored for all responses", "response_id": response_id, "updated_count": len(ids)}


@router.get("/{response_id}/similar", response_model=list[SimilarItem])
def get_similar_responses(response_id: int, top_k: int = 5):
    """
    Get top-k responses similar to the given response (same prompt, excluding self).
    Requires embeddings to be computed.
    """
    _supabase_check()
    r = supabase.table("responses").select("*").eq("id", response_id).limit(1).execute()
    if not r.data or len(r.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Response {response_id} not found")

    current = r.data[0]
    if not current.get("embedding"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response has no embedding; call POST /responses/{id}/embed first",
        )

    prompt_id = current["prompt_id"]
    others_r = (
        supabase.table("responses")
        .select("*")
        .eq("prompt_id", prompt_id)
        .neq("id", response_id)
        .execute()
    )
    others = [x for x in (others_r.data or []) if x.get("embedding")]

    others_data = [(x["id"], json.loads(x["embedding"])) for x in others]

    try:
        from services.ranking.rank import get_top_k_similar

        scored = get_top_k_similar(
            current_embedding=json.loads(current["embedding"]),
            current_response_id=response_id,
            others=others_data,
            top_k=top_k,
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Ranking not yet implemented by teammate",
        )

    id_to_row = {x["id"]: x for x in others}
    return [
        SimilarItem(id=rid, text=id_to_row[rid]["text"], score=score)
        for rid, score in scored
        if rid in id_to_row
    ]
