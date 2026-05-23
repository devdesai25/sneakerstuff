from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from services.users import login_service
from schemas.users import UserLogin,UserResponse
from database import get_db

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):

    return login_service(form_data, db)