from fastapi import APIRouter, Depends, HTTPException
from services.auth import req_admin
from services.product_service import productUpdate
from schemas.product import ProductUpdate
from sqlalchemy.orm import Session
from models.users import User
from database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Update"]
)

@router.patch("/update/{id}")
def update_product(
    id : int ,
    cur_update : ProductUpdate,
    admin : User = Depends(req_admin), 
    db : Session = Depends(get_db)
):

    return productUpdate(id, cur_update, db)