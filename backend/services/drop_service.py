from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.models.drops import Drop
from backend.models.products import Product
from backend.schemas.drops import DropCreate, DropUpdate
from backend.enums.drop_status import DropStatus, DELETABLE_STATES, STOCK_RESERVED_STATES, CANCELLABLE_STATES, PUBLISHABLE_STATES, UPDATABLE_STATES
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
            detail="Product not found"
        )
    
    if product.stock < drop_data.drop_inventory:
        raise HTTPException(
            status_code=422,
            detail="Insufficient stock"
        )
    
    if drop_data.opens_at >= drop_data.closes_at:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable entity"
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
    
    if drop.status not in UPDATABLE_STATES:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid state transition"
        )
    
    product = await get_product_or_404(drop.product_id, db)
    
    try:
        update_data = drop_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
                setattr(drop, key, value)

        if product.stock < drop.drop_inventory:
            raise HTTPException(
                status_code=422,
                detail="Insufficient stock"
            )

        if drop.opens_at >= drop.closes_at:
            raise HTTPException(
                status_code=422,
                detail="Unprocessable entity"
            )
             
        await db.commit()
        await db.refresh(drop)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
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
    
    if drop.status not in DELETABLE_STATES:
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
            detail="Database integrity error"
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

    if drop.status not in CANCELLABLE_STATES:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"
        )
    
    try:
        # restore stock only if it was actually reserved
        if drop.status in STOCK_RESERVED_STATES:
            product = await get_product_or_404(drop.product_id, db)
            product.stock += drop.drop_inventory
        
        drop.status = DropStatus.CANCELLED
        
        await db.commit()
        await db.refresh(drop)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
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

    if drop.status not in PUBLISHABLE_STATES:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"   
        )

    if drop.drop_inventory <= 0 :
        raise HTTPException(
            status_code=422,
            detail="Drop inventory cannot be zero or less than zero"
        )

    if product.stock < drop.drop_inventory:
        raise HTTPException(
            status_code=422,
            detail="Insufficient stock"
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
            detail="Database integrity error"
        )
    
    except Exception:
        await db.rollback()
        raise
    
    return drop
