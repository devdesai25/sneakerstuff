from fastapi import APIRouter, Depends, HTTPException
from services.auth import req_admin
from services.product_service import productDelete
from database import get_db
from models.products import product

router = APIRouter(
    prefix="/admin",
    tags=["delete"]
)

@router.delete("/delete/{id}")
def delete_prod(id : int,admin = Depends(req_admin), db = Depends(get_db)):

    return productDelete(id, db)