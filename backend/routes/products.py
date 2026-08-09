from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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

from backend.services.redis_service import get_cache, set_cache

@router.get("/products", response_model= list[ProductResponse])
async def get_products(
    limit: int = 10, 
    offset: int = 0,
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"products:list:{limit}:{offset}:{q or ''}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    stmt = select(Product).options(selectinload(Product.sizes))
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q}%"))
    stmt = stmt.offset(offset).limit(limit)
    
    all_prod = (await db.execute(stmt)).scalars().all()
    serialized = [
        {
            "product_id": p.product_id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "stock": p.stock,
            "images": p.images,
            "sizes": [{"id": s.id, "size": s.size, "stock": s.stock} for s in p.sizes]
        }
        for p in all_prod
    ]
    await set_cache(cache_key, serialized, ttl=60)
    return all_prod

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"product:detail:{product_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    stmt = select(Product).options(selectinload(Product.sizes)).where(Product.product_id == product_id)
    product = (await db.execute(stmt)).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    serialized = {
        "product_id": product.product_id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock": product.stock,
        "images": product.images,
        "sizes": [{"id": s.id, "size": s.size, "stock": s.stock} for s in product.sizes]
    }
    await set_cache(cache_key, serialized, ttl=60)
    return product

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