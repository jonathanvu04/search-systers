import json

from fastapi import APIRouter, HTTPException, status

from ..core.supabase import supabase
from ..schemas.response import ResponseSubmit, ResponseSubmitResult, SimilarItem

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


SEMANTIC_EMBED_DIM = 384


def _backfill_embeddings(prompt_id: int | None = None) -> dict:
    q = supabase.table("responses").select("id, text, embedding")
    if prompt_id is not None:
        q = q.eq("prompt_id", prompt_id)
    r = q.order("id").execute()
    rows = r.data or []

    to_embed = []
    for row in rows:
        text = row.get("text") or ""
        emb = row.get("embedding")
        if not text:
            continue
        needs_update = emb is None
        if not needs_update:
            try:
                parsed = json.loads(emb)
                if len(parsed) != SEMANTIC_EMBED_DIM:
                    needs_update = True
            except (json.JSONDecodeError, TypeError):
                needs_update = True
        if needs_update:
            to_embed.append((row["id"], text))

    if not to_embed:
        return {"detail": "No responses need backfill", "updated_count": 0, "prompt_id": prompt_id}

    ids = [x[0] for x in to_embed]
    texts = [x[1] for x in to_embed]

    try:
        from services.embedding.semantic import embed_batch

        vectors = embed_batch(texts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failed: {str(e)}",
        )

    for rid, vec in zip(ids, vectors):
        supabase.table("responses").update({"embedding": json.dumps([float(x) for x in vec])}).eq("id", rid).execute()

    return {"detail": "Embeddings backfilled", "updated_count": len(ids), "prompt_id": prompt_id}


@router.post("/submit", response_model=ResponseSubmitResult, status_code=status.HTTP_201_CREATED)
def submit_response(payload: ResponseSubmit):
    """
    Insert a response with semantic embedding in one atomic API call.
    """
    _supabase_check()
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response text cannot be empty",
        )

    try:
        from services.embedding.semantic import embed

        vec = embed(text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failed: {str(e)}",
        )

    row: dict[str, object] = {
        "prompt_id": payload.prompt_id,
        "text": text,
        "embedding": json.dumps([float(x) for x in vec]),
    }
    if payload.user_id:
        row["user_id"] = payload.user_id

    ins = supabase.table("responses").insert(row).execute()
    inserted_rows = ins.data or []
    response_id = inserted_rows[0].get("id") if inserted_rows else None
    if response_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Response insert failed",
        )

    # Keep the full table healthy by repairing any null/outdated embeddings on each submit.
    _backfill_embeddings(prompt_id=None)

    return ResponseSubmitResult(response_id=response_id)


@router.post("/backfill-embeddings", status_code=status.HTTP_200_OK)
def backfill_embeddings(prompt_id: int | None = None):
    """
    Recompute embeddings for responses with null or outdated (wrong dimension) embeddings.
    Use after migrating from TF-IDF to semantic. Optional prompt_id to scope to one prompt.
    """
    _supabase_check()
    return _backfill_embeddings(prompt_id=prompt_id)


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
    Compute semantic embedding for a response and store in Supabase.
    Call this after the frontend inserts a response. Only embeds the new response.
    """
    _supabase_check()
    r = supabase.table("responses").select("*").eq("id", response_id).limit(1).execute()
    if not r.data or len(r.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Response {response_id} not found")

    row = r.data[0]
    text = row.get("text")
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Response has no text")

    try:
        from services.embedding.semantic import embed

        vec = embed(text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failed: {str(e)}",
        )

    embedding_json = json.dumps([float(x) for x in vec])
    supabase.table("responses").update({"embedding": embedding_json}).eq("id", response_id).execute()
    return {"detail": "Embedding computed and stored", "response_id": response_id}


@router.get("/{response_id}/similar", response_model=list[SimilarItem])
def get_similar_responses(response_id: int, top_k: int = 4):
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
