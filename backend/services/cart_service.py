from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.models.products import Product
from backend.models.product_sizes import ProductSize
from backend.models.cart_items import CartItem
from backend.models.users import User
from backend.schemas.cart_items import CartPatch, CartCreate

async def cart_add(
    cur_cart: CartCreate,
    user: User, 
    db: AsyncSession
) -> CartItem:
    """Add to cart with validation"""
    product = (
        await db.execute(
            select(Product).where(Product.product_id == cur_cart.product_id)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code= 404,
            detail= "Product Not found"
        )
        
    product_size = (
        await db.execute(
            select(ProductSize).where(
                ProductSize.product_id == cur_cart.product_id,
                ProductSize.size == cur_cart.size
            )
        )
    ).scalar_one_or_none()
    
    if not product_size:
        raise HTTPException(
            status_code=404,
            detail="Product size not found"
        )
        
    """Check Available quantity before creating cart"""
    if product_size.stock < cur_cart.quantity:
        raise HTTPException(
            status_code= 409,
            detail="Product is out of stock"
        )
    
    cart = (
        await db.execute(
            select(CartItem).where(
                CartItem.user_id == user.id, 
                CartItem.product_id == cur_cart.product_id,
                CartItem.size == cur_cart.size
            )
        )
    ).scalar_one_or_none()
    
    if cart is None:
        try:
            add_to_cart = CartItem(
                user_id = user.id,
                product_id = cur_cart.product_id,
                quantity = cur_cart.quantity,
                size = cur_cart.size
            )

            db.add(add_to_cart)
            await db.commit()
            await db.refresh(add_to_cart)

            return add_to_cart

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Database Integrity Error"
            )
        
    if product_size.stock < (cur_cart.quantity + cart.quantity):
       raise HTTPException(
           status_code=409,
           detail = "Stock unavailable"
       ) 
   
    try:
        cart.quantity += cur_cart.quantity
        await db.commit()
        await db.refresh(cart)
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )

    return cart

async def cart_patch(
    product_id: int, 
    cur_cart: CartPatch, 
    user: User, 
    db: AsyncSession
) -> CartItem:
    """Set/Delete Product from cart"""
    product = (
        await db.execute(
            select(Product).where(Product.product_id == product_id)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code= 404,
            detail= "Product Not Found"
        )
    
    cart = (
        await db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id)
        )
    ).scalar_one_or_none() 
    
    if cart is None:
        raise HTTPException(
            status_code= 404,
            detail= "Cart Not Found"
        )

    if product.stock < cart.quantity:
        raise HTTPException(
            status_code= 409,
            detail= "Product Out of Stock"
        )
    
    try:
        if cur_cart.quantity == 0:
            await db.delete(cart)
            await db.commit()
            return {"Message": "Product Removed From Cart"}
        
        else:
            cart.quantity = cur_cart.quantity
            await db.commit()
            await db.refresh(cart)

            return cart
    
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code= 409,
            detail= "Database Integrity Error"
        )

async def cart_delete(
    product_id: int, 
    user: User, 
    db: AsyncSession
) -> dict:
    """Delete Product from Cart"""
    cart = (
        await db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id)
        )
    ).scalar_one_or_none()

    if cart is None:
        raise HTTPException(
            status_code= 404,
            detail= "Cart Not Found"
        )
    
    try:
        await db.delete(cart)
        await db.commit()
    
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code= 409,
            detail= "Database Integrity Error"
        )
    
    return {"Message": "Product Deleted From Cart Successfully"}