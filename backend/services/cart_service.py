from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.models.products import Product
from backend.models.product_sizes import ProductSize
from backend.models.cart_items import CartItem
from backend.models.users import User
from backend.schemas.cart_items import CartPatch, CartCreate

from sqlalchemy.dialects.postgresql import insert as pg_insert

async def cart_add(
    cur_cart: CartCreate,
    user: User, 
    db: AsyncSession
) -> CartItem:
    """Add to cart with atomic PostgreSQL Upsert"""
    product = (
        await db.execute(
            select(Product).where(Product.product_id == cur_cart.product_id)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product.is_reserved_for_drop:
        raise HTTPException(
            status_code=400,
            detail="This sneaker is reserved for an upcoming drop and cannot be purchased directly"
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
        
    if product_size.stock < cur_cart.quantity:
        raise HTTPException(
            status_code=409,
            detail="Product is out of stock"
        )

    stmt = (
        pg_insert(CartItem)
        .values(
            user_id=user.id,
            product_id=cur_cart.product_id,
            quantity=cur_cart.quantity,
            size=cur_cart.size
        )
        .on_conflict_do_update(
            constraint="unique_user_product_size",
            set_={"quantity": CartItem.quantity + cur_cart.quantity}
        )
        .returning(CartItem)
    )

    try:
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )

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