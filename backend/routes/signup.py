from fastapi import APIRouter, Depends
from schemas.users import UserSignup
from services.users import signup_service
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    tags=["signup"]
)

@router.post("/signup")
def signup(user:UserSignup, db : Session = Depends(get_db)):
    
    return signup_service(user, db) 