from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.models.order import Order
from backend.models.users import User
from backend.models.products import Product
from backend.models.product_sizes import ProductSize

async def get_orders_all_or_404(
    user: User, 
    db: AsyncSession
) -> list[Order]:
    
    orders = (
        await db.execute(
            select(Order)
            .where(Order.user_id == user.id)
            .options(selectinload(Order.order_items))
        )
    ).scalars().all()

    if not orders:
        raise HTTPException(
            status_code=404,
            detail="Orders not found"
        )
    return orders

async def get_order_one_or_404(
    order_id: int,
    user: User, 
    db: AsyncSession
) -> Order:
    
    order = (
        await db.execute(
            select(Order)
            .where(Order.order_id == order_id, Order.user_id == user.id)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.reservation)
            )
        )
    ).scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Orders not found"
        )
    return order

async def restore_stock(order: Order, db: AsyncSession):

    for item in order.order_items:
        product = (
            await db.execute(
                select(Product).where(Product.product_id == item.product_id)
            )
        ).scalar_one_or_none() 
        if product:
            product.stock += item.quantity
            
            if item.size:
                product_size = (
                    await db.execute(
                        select(ProductSize).where(
                            ProductSize.product_id == item.product_id,
                            ProductSize.size == item.size
                        )
                    )
                ).scalar_one_or_none()
                if product_size:
                    product_size.stock += item.quantity
