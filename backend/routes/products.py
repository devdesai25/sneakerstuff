from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.auth import req_admin
from backend.models.users import User
from backend.models.products import Product
from backend.schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductUpdate
)
from backend.services.product_service import (
    product_add, 
    product_delete, 
    product_update
)

router = APIRouter(
    tags=["Product"]
)

@router.get("/")
def home():
    return {"message":"backend connected"}

@router.get("/products", response_model= list[ProductResponse])
async def get_products(
    limit: int = 10, 
    offset: int = 0,
    db: AsyncSession = Depends(get_db )
):
    
    all_prod = (
        await db.execute(
            select(Product)
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()

    return all_prod

@router.post("/admin/create", response_model = ProductResponse)
async def create_product(
    new_product: ProductCreate,
    admin: User = Depends(req_admin), 
    db: AsyncSession = Depends(get_db)
):
    
    return await product_add(new_product, admin, db)

@router.delete("/admin/delete/{product_id}")
async def delete_prod(
    product_id: int,
    admin: User = Depends(req_admin),
    db: AsyncSession =  Depends(get_db)
):

    return await product_delete(product_id, db)

@router.patch("/admin/update/{product_id}", response_model = ProductResponse)
async def update_product(
    product_id: int ,
    cur_update: ProductUpdate,
    admin: User = Depends(req_admin), 
    db: AsyncSession = Depends(get_db)
):

    return await product_update(product_id, cur_update, db)