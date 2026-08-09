from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from backend.models.products import Product
from backend.models.users import User
from backend.models.drops import Drop
from backend.models.product_sizes import ProductSize
from backend.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from backend.helpers.product_helpers import get_product_or_404

async def product_add(
    new_product: ProductCreate, 
    admin: User,
    db: AsyncSession
) -> ProductResponse:
    """Create a new product with duplicate check"""
    product = (
        await db.execute(
            select(Product)
            .where(Product.name == new_product.name)
        )
    ).scalar_one_or_none()

    if product :
        raise HTTPException(
            status_code=409,
            detail="Duplicate Value Inserted"
        )

    stock = new_product.stock
    if hasattr(new_product, 'sizes') and new_product.sizes:
        stock = sum(size.stock for size in new_product.sizes)

    add_prod = Product(
        name = new_product.name, 
        description = new_product.description, 
        price = new_product.price, 
        stock = stock, 
        created_by = admin.id,
        images = new_product.images
    ) 
    
    try:
        db.add(add_prod)
        await db.commit()
        await db.refresh(add_prod)

        if hasattr(new_product, 'sizes') and new_product.sizes:
            for size_data in new_product.sizes:
                new_size = ProductSize(
                    product_id=add_prod.product_id,
                    size=size_data.size,
                    stock=size_data.stock
                )
                db.add(new_size)
            await db.commit()

        # load sizes for response
        stmt = select(Product).options(selectinload(Product.sizes)).where(Product.product_id == add_prod.product_id)
        result = await db.execute(stmt)
        add_prod = result.scalar_one()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            409,
            detail="Database Integrity Error"
        )
    except Exception:
        await db.rollback()
        raise
    return add_prod

async def product_delete(
    product_id: int, 
    db: AsyncSession
) -> dict :
    """Delete a product"""
    product = await get_product_or_404(product_id, db)
    
    drop = (
        await db.execute(
            select(Drop)
            .where(Drop.product_id == product.product_id)
        )
    ).scalars().all()

    if drop:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a product that is used in a drop"
        )
    
    try:
        await db.delete(product)
        await db.commit()

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
    """Update a product"""
    product = await get_product_or_404(product_id, db)

    """Skip fields client hasnt sent"""
    """Convert Pydantic model to dict, only with fields client sent"""
    update_data = update_product.model_dump(exclude_unset=True)

    sizes_data = update_data.pop('sizes', None)

    for key, value in update_data.items():
            setattr(product, key, value)
            
    if sizes_data is not None:
        from sqlalchemy import delete
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