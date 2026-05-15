from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.user import User
from app.services.taxonomy import get_taxonomy

router = APIRouter(prefix="/api/metadata", tags=["metadata"])


@router.get("")
def get_metadata(current_user: User = Depends(get_current_user)):
    """Returns all taxonomy/master data for frontend dropdowns."""
    return get_taxonomy()
