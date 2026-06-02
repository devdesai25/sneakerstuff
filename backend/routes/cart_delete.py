from fastapi import APIRouter, Depends
from database import get_db
from sqlalchemy.orm import Session
from models.users import User
from services.auth import get_current_user
from services.cart_service import cartDelete
router = APIRouter()

@router.delete("/cart/{id}")
def delete_cart(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    return  cartDelete(id, user, db)