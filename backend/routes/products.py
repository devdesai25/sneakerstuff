from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductUpdate
)
from backend.models.users import User
from backend.models.products import Product
from backend.services.auth import req_admin
from backend.services.product_service import (
    productadd, 
    productDelete, 
    productUpdate
)



router = APIRouter(
    prefix="/admin",
    tags=["Create"]
)

@router.get("/")
def home():
    return {"message":"backend connected"}

@router.get("/products", response_model= list[ProductResponse])
def get_products(
    limit : int = 10, 
    offset : int = 0,
    db: Session = Depends(get_db )
):
    
    all_prod = db.query(Product).offset(offset).limit(limit).all()
    
    return all_prod

@router.post("/create")
def create_product(
    cur_product : ProductCreate,
    admin : User = Depends(req_admin), 
    db : Session = Depends(get_db)
):
    
    return productadd(cur_product, admin, db)

@router.delete("/delete/{id}")
def delete_prod(
    id : int,
    admin : User = Depends(req_admin),
    db : Session =  Depends(get_db)
):

    return productDelete(id, db)

@router.patch("/update/{id}")
def update_product(
    id : int ,
    cur_update : ProductUpdate,
    admin : User = Depends(req_admin), 
    db : Session = Depends(get_db)
):

    return productUpdate(id, cur_update, db)