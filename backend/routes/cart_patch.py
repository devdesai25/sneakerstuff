from fastapi import APIRouter, Depends
from services.cart_service import cartPatch
from schemas.cart_items import CartPatch
from database import get_db
from sqlalchemy.orm import Session
from models.users import User
from services.auth import get_current_user

router = APIRouter(tags=["Cart Update"])

@router.patch("/cart/{id}")
def patch_cart(
    id: int, 
    cart: CartPatch, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    
    return cartPatch(id, cart, user, db)