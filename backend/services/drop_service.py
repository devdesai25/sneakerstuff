from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.models.drops import Drop
from backend.models.products import Product
from backend.schemas.drops import DropCreate
from backend.enums.drop_status import DropStatus
from backend.tasks.drop_tasks import activate_drop, close_drop
from backend.helpers.drop_helpers import get_drop_or_404, drop_get

async def drop_create(
    drop_data: DropCreate, 
    db: AsyncSession
) -> Drop:

    product = (
        await db.execute(
            select(Product).where(Product.product_id == drop_data.product_id)
        )
    ).scalar_one_or_none()
    """(
        db.query(Product)
        .filter(Product.product_id == drop_data.product_id)
        .first()
    )    """

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
            status = DropStatus.DRAFT
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
    drop_data: DropCreate, 
    db:AsyncSession
)-> Drop:

    drop = await get_drop_or_404(drop_id, db)
    
    if drop.status != DropStatus.DRAFT:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid state transition"
        )
    
    try:
        update_data = drop_data.model_dump(exclude_unset=True)

        for key,value in update_data.items():
            if hasattr(drop, key):
                setattr(drop, key, value)

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

    if drop.status != DropStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"
        )
    
    try:
        drop.status = DropStatus.SCHEDULED        
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
