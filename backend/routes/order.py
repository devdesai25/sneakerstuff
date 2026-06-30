from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.orders import OrderRequest, OrderResponse
from backend.models.users import User
from backend.services.auth import get_current_user
from backend.services.order_service import (
    orderCreate, 
    orderGet, 
    orderPay, 
    orderCancel
)

router = APIRouter(tags=["Order"])

@router.get("/orders", response_model=list[OrderResponse])
def get_order(
    user: User=Depends(get_current_user),
    db: Session=Depends(get_db)
):
    
    return orderGet(user, db)

@router.post("/orders", response_model = OrderResponse)
def create_order(
    address: OrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return orderCreate(address, user, db)

@router.patch("/orders/{id}/pay", response_model = OrderResponse)
def pay_order(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return orderPay(id, user, db)

@router.patch("/orders/{id}/cancel", response_model = OrderResponse)
def cancel_order(
    id:int,
    user:User=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    return orderCancel(id, user, db)