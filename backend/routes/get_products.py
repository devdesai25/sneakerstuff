from fastapi import APIRouter, Depends
from database import get_db
from models.products import Product
from schemas.product import ProductResponse
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["product"]
)

@router.get("/products", response_model= list[ProductResponse])
def get_products(
    limit : int = 10, 
    offset : int = 0,
    db: Session = Depends(get_db )
):
    
    all_prod = db.query(Product).offset(offset).limit(limit).all()
    
    return all_prod