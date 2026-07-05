# ==========================================
# SNEAKERSTUFF AUTH REFACTOR
# Modified by Sneakerstuff Developer
# Purpose:
# Drop service operations.
# ==========================================

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.models.drops import Drop
from backend.models.products import Product
from backend.schemas.drops import DropCreate, DropUpdate
from backend.enums.drop_status import DropStatus
from backend.tasks.drop_tasks import activate_drop, close_drop
from backend.helpers.drop_helpers import get_drop_or_404, drop_get
from backend.helpers.product_helpers import get_product_or_404

async def drop_create(
    drop_data: DropCreate, 
    db: AsyncSession
) -> Drop:

    product = (
        await db.execute(
            select(Product).where(Product.product_id == drop_data.product_id)
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )
    
    if product.stock < drop_data.drop_inventory:
        raise HTTPException(
            status_code=422,
            detail="Infsufficient Stock"
        )
    
    if drop_data.opens_at >= drop_data.closes_at:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity"
        )
    
    try:
        new_drop = Drop(
            product_id = drop_data.product_id,
            opens_at = drop_data.opens_at,
            closes_at = drop_data.closes_at,
            drop_inventory = drop_data.drop_inventory,
            product_name = product.name,
            product_price = product.price,
            product_image = product.images,
            status = DropStatus.DRAFT,
            is_visible = drop_data.is_visible
        )

        db.add(new_drop)
        await db.commit()
        await db.refresh(new_drop)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    except Exception:
        await db.rollback()
        raise

    return new_drop

async def drop_update(
    drop_id: int, 
    drop_data: DropUpdate, 
    db: AsyncSession
)-> Drop:

    drop = await get_drop_or_404(drop_id, db)
    
    if drop.status != DropStatus.DRAFT:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid state transition"
        )
    
    product = await get_product_or_404(drop.product_id, db)
    
    try:
        update_data = drop_data.model_dump(exclude_unset=True)

        for key,value in update_data.items():
            if hasattr(drop, key):
                setattr(drop, key, value)

        if product.stock < drop.drop_inventory:
            raise HTTPException(
                status_code=422,
                detail="Insufficient Stock"
            )

        if drop.opens_at >= drop.closes_at:
            raise HTTPException(
                status_code=422,
                detail="Unprocessable Entity"
            )
             
        await db.commit()
        await db.refresh(drop)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    except Exception:
        await db.rollback()
        raise

    return drop

async def drop_delete(
    drop_id: int, 
    db: AsyncSession
) -> Drop:
    
    drop = await get_drop_or_404(drop_id, db)
    
    if drop.status != DropStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"
        )
    
    try:
        product = await get_product_or_404(drop.product_id, db)
        product.stock += drop.drop_inventory
        drop.drop_inventory -= drop.drop_inventory
        await db.delete(drop)
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
    
    return drop

async def drop_cancel(
    drop_id: int, 
    db: AsyncSession
) -> Drop:
    
    drop = await get_drop_or_404(drop_id, db)

    if drop.status != DropStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"
        )
    
    try:
        product = await get_product_or_404(drop.product_id, db)
        product.stock += drop.drop_inventory
        drop.drop_inventory -= drop.drop_inventory
        drop.status = DropStatus.CANCELLED
        
        await db.commit()
        await db.refresh(drop)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    except Exception:
        await db.rollback()
        raise

    return drop

async def drop_publish(
    drop_id: int, 
    db: AsyncSession
) -> Drop:
    
    drop = await get_drop_or_404(drop_id, db)

    product = (
        await db.execute(
            select(Product)
            .where(Product.product_id == drop.product_id)
        )
    ).scalar_one_or_none()

    if drop.status != DropStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"
    
        )
    if drop.drop_inventory < 0 :
        raise HTTPException(
            status_code=422,
            detail="Drop inventory cannot be zero or less than zero"
        )
    if product.stock <=  drop.drop_inventory:
        raise HTTPException(
            status_code=422,
            detail="Insufficient Stock"
        )
    
    try:
        drop.status = DropStatus.SCHEDULED 
        product.stock -= drop.drop_inventory           
        await db.commit()
        await db.refresh(drop)
        
        activate_drop.apply_async(
            args=[drop.drop_id],
            eta=drop.opens_at,
        )

        close_drop.apply_async(
            args=[drop.drop_id],
            eta=drop.closes_at,
        )
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    except Exception:
        await db.rollback()
        raise
    
    return drop
