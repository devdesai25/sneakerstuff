from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.orders import OrderRequest, OrderResponse
from backend.models.users import User
from backend.services.auth import get_current_user
from backend.services.order_service import (
    order_create, order_get, 
    order_pay, order_cancel
)

router = APIRouter(tags=["Order"])

@router.get("/orders", response_model=list[OrderResponse])
async def get_order(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    return await order_get(user, db)

@router.post("/orders", response_model = OrderResponse)
async def create_order(
    address: OrderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await order_create(address, user, db)

@router.patch("/orders/{order_id}/pay", response_model = OrderResponse)
async def pay_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    return await order_pay(order_id, user, db)

@router.patch("/orders/{id}/cancel", response_model = OrderResponse)
async def cancel_order(
    id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await order_cancel(id, user, db)