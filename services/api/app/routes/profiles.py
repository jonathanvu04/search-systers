from fastapi import APIRouter, HTTPException, status

from ..core.supabase import supabase
from ..schemas.profile import ProfileRead

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _supabase_check():
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase not configured.",
        )


@router.get("/", response_model=list[ProfileRead])
def list_profiles():
    """List all profiles."""
    _supabase_check()
    r = supabase.table("profiles").select("*").order("created_at").execute()
    return r.data or []


@router.get("/{profile_id}", response_model=ProfileRead)
def get_profile(profile_id: str):
    """Fetch a single profile by UUID."""
    _supabase_check()
    r = (
        supabase.table("profiles")
        .select("*")
        .eq("id", profile_id)
        .limit(1)
        .execute()
    )
    if not r.data or len(r.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {profile_id} not found",
        )
    return r.data[0]
