from fastapi import APIRouter, Depends

from backend.schemas.cart_items import CartResponse, CartCreate, CartPatch
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.cart_items import CartItem
from backend.models.users import User
from backend.schemas.cart_items import (
    CartResponse, 
    CartCreate, 
    CartPatch
)
from backend.services.auth import get_current_user
from backend.services.cart_service import (
    cartAdd, 
    cartDelete, 
    cartPatch
)


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

@router.post("/cart")
def create_cart(
    cart: CartCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    return cartAdd(cart, user, db)

@router.delete("/cart/{id}")
def delete_cart(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    return  cartDelete(id, user, db)

@router.patch("/cart/{id}")
def patch_cart(
    id: int, 
    cart: CartPatch, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    
    return cartPatch(id, cart, user, db)