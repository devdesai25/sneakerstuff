from fastapi import APIRouter, Depends
from database import get_db
from services.auth import get_current_user
from services.order_service import orderCreate
from sqlalchemy.orm import Session
from schemas.orders import OrderRequest
from models.users import User

router = APIRouter(tags=["Checkout"])

@router.post("/checkout")
def create_order(
    address: OrderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return orderCreate(address, user, db)