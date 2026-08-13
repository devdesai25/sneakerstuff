from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.helpers.product_helpers import get_product_or_404
from backend.models.drops import Drop
from backend.models.product_sizes import ProductSize
from backend.models.products import Product
from backend.models.users import User
from backend.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from backend.services.redis_service import invalidate_cache


async def product_add(
    new_product: ProductCreate, 
    admin: User,
    db: AsyncSession
) -> ProductResponse:
    """Create a new product with duplicate check and associated sizes in a single transaction."""
    product = (
        await db.execute(
            select(Product).where(Product.name == new_product.name)
        )
    ).scalar_one_or_none()

    if product:
        raise HTTPException(
            status_code=409,
            detail="Duplicate Value Inserted"
        )

    stock = new_product.stock
    if hasattr(new_product, 'sizes') and new_product.sizes:
        stock = sum(size.stock for size in new_product.sizes)

    add_prod = Product(
        name=new_product.name, 
        description=new_product.description, 
        price=new_product.price, 
        stock=stock, 
        created_by=admin.id,
        images=new_product.images,
        is_reserved_for_drop=getattr(new_product, 'is_reserved_for_drop', False),
        is_visible=getattr(new_product, 'is_visible', True)
    ) 
    
    try:
        db.add(add_prod)
        await db.flush()

        if hasattr(new_product, 'sizes') and new_product.sizes:
            for size_data in new_product.sizes:
                new_size = ProductSize(
                    product_id=add_prod.product_id,
                    size=size_data.size,
                    stock=size_data.stock
                )
                db.add(new_size)
            await db.flush()

        await db.commit()

        # Load product with sizes for response serialization
        stmt = select(Product).options(selectinload(Product.sizes)).where(Product.product_id == add_prod.product_id)
        result = await db.execute(stmt)
        add_prod = result.scalar_one()

        await invalidate_cache("products:*")
        await invalidate_cache("product:*")

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    except Exception:
        await db.rollback()
        raise

    return add_prod


async def product_delete(
    product_id: int, 
    db: AsyncSession
) -> dict:
    """Delete a product after validating no active drop references it."""
    product = await get_product_or_404(product_id, db)
    
    # Check drop existence with limit(1) instead of fetching all records
    drop_exists = (
        await db.execute(
            select(Drop.drop_id)
            .where(Drop.product_id == product.product_id)
            .limit(1)
        )
    ).scalar_one_or_none()

    if drop_exists:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a product that is used in a drop"
        )
    
    try:
        await db.delete(product)
        await db.commit()

        await invalidate_cache("products:*")
        await invalidate_cache("product:*")

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    except Exception:
        await db.rollback()
        raise

    return {
        "message": "Product deleted successfully"
    }


async def product_update(
    product_id: int, 
    update_product: ProductUpdate, 
    db: AsyncSession
) -> ProductResponse:
    """Update product fields and sizes atomically."""
    product = await get_product_or_404(product_id, db)

    update_data = update_product.model_dump(exclude_unset=True)
    sizes_data = update_data.pop('sizes', None)

    for key, value in update_data.items():
        setattr(product, key, value)
            
    if sizes_data is not None:
        await db.execute(delete(ProductSize).where(ProductSize.product_id == product_id))
        
        new_stock = 0
        for size_data in sizes_data:
            size = size_data['size'] if isinstance(size_data, dict) else size_data.size
            stock = size_data['stock'] if isinstance(size_data, dict) else size_data.stock
            new_stock += stock
            db.add(ProductSize(
                product_id=product_id,
                size=size,
                stock=stock
            ))
            
        product.stock = new_stock
    
    try:
        await db.commit()
        
        stmt = select(Product).options(selectinload(Product.sizes)).where(Product.product_id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one()

        await invalidate_cache("products:*")
        await invalidate_cache("product:*")
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    except Exception:
        await db.rollback()
        raise
    
    return product