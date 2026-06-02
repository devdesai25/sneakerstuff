from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.users import User
from schemas.cart_items import CartCreate
from services.auth import get_current_user
from database import get_db
from services.cart_service import cartAdd
router = APIRouter(
    tags=["Add to Cart"]
    )

@router.post("/cart")
def create_cart(
    cart: CartCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    return cartAdd(cart, user, db)