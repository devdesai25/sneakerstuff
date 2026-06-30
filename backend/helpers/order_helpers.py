from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.order import Order
from backend.models.users import User

async def get_orders_all_or_404(
    user: User, 
    db: AsyncSession
) -> list[Order]:
    
    orders = (
        await db.execute(
            select(Order).where(Order.user_id == user.id)
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
            select(Order).where(Order.order_id == order_id, Order.user_id == user.id)
        )
    ).scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Orders not found"
        )
    return order