from fastapi import APIRouter, Depends
from database import get_db
from services.auth import get_current_user
from services.order_service import orderCreate, orderGet, orderPay, orderCancel
from sqlalchemy.orm import Session
from schemas.orders import OrderRequest
from models.users import User

router = APIRouter(tags=["Order"])

@router.get("/orders")
def get_order(
    user: User=Depends(get_current_user),
    db:Session=Depends(get_db)
    ):
    
    return orderGet(user, db)

@router.post("/orders")
def create_order(
    address: OrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return orderCreate(address, user, db)

@router.patch("/orders/{id}/pay")
def pay_order(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return orderPay(id, user, db)

@router.patch("/orders/{id}/cancel")
def cancel_order(
    id:int,
    user:User=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    return orderCancel(id, user, db)