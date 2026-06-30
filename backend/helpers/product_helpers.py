from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.products import Product

async def get_product_or_404(
    product_id: int,
    db: AsyncSession
) -> Product:
    
    product = (
        await db.execute(
            select(Product)
            .where(Product.product_id == product_id)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    
    return product