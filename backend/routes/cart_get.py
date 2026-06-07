from fastapi import APIRouter, Depends
from database import get_db
from schemas.cart_items import CartResponse
from sqlalchemy.orm import Session
from models.cart_items import CartItem
from services.auth import get_current_user
from models.users import User

router = APIRouter(
    tags=["userCart"])

@router.get("/cart", response_model= list[CartResponse])
def get_cart(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    
    cart = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    return [{
        "product_id": item.product.product_id,
        "name": item.product.name,
        "price": item.product.price,
        "image": item.product.images,
        "quantity": item.quantity
    }
    for item in cart
    ]