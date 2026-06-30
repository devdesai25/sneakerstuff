from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.users import login_service, signup_service
from backend.schemas.users import UserLogin, UserResponse, UserSignup


router = APIRouter(
    tags=["Auth"]
)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db),
):

    return await login_service(form_data, db)


@router.post("/signup")
async def signup(
    user:UserSignup, 
    db: AsyncSession = Depends(get_db),
):
    
    return await signup_service(user, db) 