from fastapi import APIRouter, Depends, HTTPException
from services.auth import req_admin
from services.product_service import productDelete
from sqlalchemy.orm import Session
from models.users import User
from database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["delete"]
)

@router.delete("/delete/{id}")
def delete_prod(
    id : int,
    admin : User = Depends(req_admin),
    db : Session =  Depends(get_db)
):

    return productDelete(id, db)