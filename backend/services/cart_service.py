from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.models.products import Product
from backend.models.cart_items import CartItem

async def cartAdd(
        cur_cart,
        user, 
        db: AsyncSession
    ):
    """Add to cart with validation"""
    product = (
        await db.execute(
            select(Product).where(Product.product_id == cur_cart.product_)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code= 404,
            detail= "Product Not found"
        )
    """Check Available quantity before creating cart"""
    if product.stock < cur_cart.quantity:
        raise HTTPException(
            status_code= 409,
            detail="Product is out of stock"
        )
    
    cart = (
        await db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == cur_cart.product_id)
        )
    ).scalar_one_or_none()
    
    if cart is None:
        try:
            add_to_cart = CartItem(
                user_id = user.id,
                product_id = cur_cart.product_id,
                quantity = cur_cart.quantity
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
        
    if product.stock < (cur_cart.quantity + cart.quantity):
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

async def cartPatch(
        id: int, 
        cur_cart, 
        user, 
        db: AsyncSession
    ):
    """Set/Delete Product from cart"""
    product = (
        await db.execute(
            select(Product).where(Product.product_id == id)
        )
    ).scalar_one_or_none()
    """ (
        db.query(Product)
        .filter(Product.product_id == id)
        .first()
    )
    """
    if not product:
        raise HTTPException(
            status_code= 404,
            detail= "Product Not Found"
        )
    
    cart = (
        await db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == id)
        )
    ).scalar_one_or_none() 
    """(
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.product_id == id)
        .first()
    )"""

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

async def cartDelete(
        id: int, 
        user, 
        db: AsyncSession
    ):
    """Delete Product from Cart"""
    cart = (
        await db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == id)
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