from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.cart_items import CartResponse, CartCreate, CartPatch
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
    cart_add, 
    cart_delete, 
    cart_patch
)


router = APIRouter(
    tags=["userCart"])

@router.get("/cart", response_model= list[CartResponse])
async def get_cart(
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
) -> dict:
    
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user.id)
        .options(selectinload(CartItem.product))
    )
    
    cart = result.scalars().all()
    
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
async def create_cart(
    cart: CartCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    return await cart_add(cart, user, db)

@router.delete("/cart/{product_id}")
async def delete_cart(
    product_id: int, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    
    return await cart_delete(product_id, user, db)

@router.patch("/cart/{product_id}")
async def patch_cart(
    product_id: int, 
    cart: CartPatch, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    
    return await cart_patch(product_id, cart, user, db)