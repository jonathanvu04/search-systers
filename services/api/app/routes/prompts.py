from fastapi import APIRouter, HTTPException, status

from ..core.supabase import supabase
from ..schemas.prompt import PromptCreate, PromptRead

router = APIRouter(prefix="/prompts", tags=["prompts"])


def _supabase_check():
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_prompts():
    """Insert example prompts if none exist."""
    _supabase_check()
    r = supabase.table("prompts").select("id").limit(1).execute()
    if r.data and len(r.data) > 0:
        return {"detail": "Prompts already seeded"}

    supabase.table("prompts").insert({"text": "What is your why?"}).execute()
    return {"detail": "Seeded 1 prompt"}


@router.post("/", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
def create_prompt(payload: PromptCreate):
    """Create a prompt."""
    _supabase_check()
    r = (
        supabase.table("prompts")
        .select("*")
        .eq("text", payload.text)
        .limit(1)
        .execute()
    )
    if r.data and len(r.data) > 0:
        return r.data[0]

    ins = supabase.table("prompts").insert({"text": payload.text}).execute()
    return ins.data[0]


@router.get("/", response_model=list[PromptRead])
def list_prompts():
    """List all prompts ordered by id."""
    _supabase_check()
    r = supabase.table("prompts").select("*").order("id").execute()
    return r.data or []


@router.get("/{prompt_id}", response_model=PromptRead)
def get_prompt_by_id(prompt_id: int):
    """Fetch a prompt by ID."""
    _supabase_check()
    r = supabase.table("prompts").select("*").eq("id", prompt_id).limit(1).execute()
    if not r.data or len(r.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} not found")
    return r.data[0]


@router.get("/{prompt_id}/responses")
def get_responses_by_age(
    prompt_id: int,
    age_min: int | None = None,
    age_max: int | None = None,
):
    """
    Fetch responses for a prompt, optionally filtered by the responder's age.

    Joins responses → profiles to get age. Responses without a linked profile
    are excluded when an age filter is active.
    """
    _supabase_check()

    r = (
        supabase.table("responses")
        .select("id, text, user_id, profiles(name, age)")
        .eq("prompt_id", prompt_id)
        .order("id")
        .execute()
    )
    rows = r.data or []

    results = []
    for row in rows:
        profile = row.get("profiles")
        age = profile.get("age") if profile else None
        name = profile.get("name") if profile else None

        if age_min is not None or age_max is not None:
            if age is None:
                continue
            if age_min is not None and age < age_min:
                continue
            if age_max is not None and age > age_max:
                continue

        results.append({
            "id": row["id"],
            "text": row["text"],
            "name": name,
            "age": age,
        })

    return results


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: int):
    """Delete a prompt by ID."""
    _supabase_check()
    r = supabase.table("prompts").select("id").eq("id", prompt_id).limit(1).execute()
    if not r.data or len(r.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} not found")
    supabase.table("prompts").delete().eq("id", prompt_id).execute()
    return None
