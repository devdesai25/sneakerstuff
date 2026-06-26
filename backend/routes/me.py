from fastapi import APIRouter,Depends
from backend.services.auth import get_current_user
from backend.models.users import User

router = APIRouter(
    tags=["mepage"]
)

@router.get("/me")
def get_me(
    current_user : User = Depends(get_current_user)
):
    return current_user