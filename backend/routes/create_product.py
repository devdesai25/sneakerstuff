from fastapi import APIRouter, Depends
from services.product_service import productadd
from services.auth import req_admin
from schemas.product import ProductCreate
from sqlalchemy.orm import Session
from models.users import User
from database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Create"]
)

@router.post("/create")
def create_product(
    cur_product : ProductCreate,
    admin : User = Depends(req_admin), 
    db : Session = Depends(get_db)
):
    
    return productadd(cur_product, admin, db)