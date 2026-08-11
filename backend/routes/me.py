from fastapi import APIRouter, Depends

from backend.services.auth import get_current_user
from backend.models.users import User
from backend.schemas.users import UserResponse

router = APIRouter(
    tags=["mepage"]
)

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user : User = Depends(get_current_user)
):
    return current_user