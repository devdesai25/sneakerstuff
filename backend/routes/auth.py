from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from services.users import login_service, signup_service
from schemas.users import UserLogin, UserResponse, UserSignup
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):

    return login_service(form_data, db)


@router.post("/signup")
def signup(user:UserSignup, db : Session = Depends(get_db)):
    
    return signup_service(user, db) 