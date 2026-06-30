from fastapi import APIRouter,Depends

from backend.services.auth import get_current_user
from backend.models.users import User

router = APIRouter(
    tags=["mepage"]
)

@router.get("/me")
async def get_me(
    current_user : User = Depends(get_current_user)
):
    return await current_user