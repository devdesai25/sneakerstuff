from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
) -> dict:
    drop = await get_drop_or_404(drop_id, db)
    
    if drop.status not in DELETABLE_STATES:
        raise HTTPException(
            status_code=400,
            detail="Invalid state transition"
        )
    
    try:
        from backend.models.entry import Entry
        from backend.models.reservations import Reservation
        from backend.models.order import Order
        from backend.models.order_items import OrderItem
        from backend.models.products import Product
        from backend.enums.order_status import OrderStatus

        # Find all entries for this drop
        entries_stmt = select(Entry).where(Entry.drop_id == drop.drop_id)
        entries = (await db.execute(entries_stmt)).scalars().all()
        entry_ids = [e.entry_id for e in entries]

        # Restore reserved stock if drop was in any stock-reserved status
        if drop.status in STOCK_RESERVED_STATES:
            product = (
                await db.execute(
                    select(Product).where(Product.product_id == drop.product_id)
                )
            ).scalar_one_or_none()

            if product:
                restored_stock = drop.drop_inventory

                if entry_ids:
                    res_stmt = select(Reservation).where(Reservation.entry_id.in_(entry_ids))
                    reservations = (await db.execute(res_stmt)).scalars().all()
                    order_ids = [r.order_id for r in reservations if r.order_id]

                    if order_ids:
                        orders_stmt = select(Order).where(Order.order_id.in_(order_ids), Order.status == OrderStatus.PENDING).options(selectinload(Order.order_items))
                        pending_orders = (await db.execute(orders_stmt)).scalars().all()

                        for p_order in pending_orders:
                            qty = sum(item.quantity for item in p_order.order_items) if p_order.order_items else 1
                            restored_stock += qty

                product.stock += restored_stock

        # Delete associated records in strict foreign key dependency order
        if entry_ids:
            res_stmt = select(Reservation).where(Reservation.entry_id.in_(entry_ids))
            reservations = (await db.execute(res_stmt)).scalars().all()
            for res in reservations:
                if res.order_id:
                    pending_order = (
                        await db.execute(
                            select(Order)
                            .where(Order.order_id == res.order_id, Order.status == OrderStatus.PENDING)
                            .options(selectinload(Order.order_items))
                        )
                    ).scalar_one_or_none()

                    if pending_order:
                        for item in pending_order.order_items:
                            await db.delete(item)
                        await db.delete(pending_order)

                await db.delete(res)

            await db.flush()

            for entry in entries:
                await db.delete(entry)

            await db.flush()

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
    
    return {"message": "Drop deleted successfully and reserved stock restored."}

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
        from backend.models.entry import Entry
        from backend.models.reservations import Reservation
        from backend.models.order import Order
        from backend.models.products import Product
        from backend.enums.order_status import OrderStatus

        # restore stock only if it was actually reserved
        if drop.status in STOCK_RESERVED_STATES:
            product = await get_product_or_404(drop.product_id, db)

            restored_stock = drop.drop_inventory

            # Find all entries for this drop
            entries_stmt = select(Entry).where(Entry.drop_id == drop.drop_id)
            entries = (await db.execute(entries_stmt)).scalars().all()
            entry_ids = [e.entry_id for e in entries]

            if entry_ids:
                res_stmt = select(Reservation).where(Reservation.entry_id.in_(entry_ids))
                reservations = (await db.execute(res_stmt)).scalars().all()
                order_ids = [r.order_id for r in reservations if r.order_id]

                if order_ids:
                    orders_stmt = select(Order).where(Order.order_id.in_(order_ids), Order.status == OrderStatus.PENDING).options(selectinload(Order.order_items))
                    pending_orders = (await db.execute(orders_stmt)).scalars().all()

                    for p_order in pending_orders:
                        qty = sum(item.quantity for item in p_order.order_items) if p_order.order_items else 1
                        restored_stock += qty
                        p_order.status = OrderStatus.CANCELLED

            product.stock += restored_stock
            drop.drop_inventory = 0
        
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
        
        activate_drop.apply_async(
            args=[drop.drop_id],
            eta=drop.opens_at,
        )

        close_drop.apply_async(
            args=[drop.drop_id],
            eta=drop.closes_at,
        )

        await db.commit()
        await db.refresh(drop)
    
    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )
    
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue drop tasks to Celery broker: {str(exc)}"
        )
    
    return drop

async def drop_pause(
    drop_id: int,
    db: AsyncSession
) -> Drop:
    drop = await get_drop_or_404(drop_id, db)

    if drop.status not in (DropStatus.SCHEDULED, DropStatus.ENTRY_OPEN):
        raise HTTPException(
            status_code=400,
            detail="Cannot pause drop in current state"
        )

    try:
        drop.status = DropStatus.PAUSED
        await db.commit()
        await db.refresh(drop)
    except Exception:
        await db.rollback()
        raise

    return drop

async def drop_resume(
    drop_id: int,
    db: AsyncSession
) -> Drop:
    drop = await get_drop_or_404(drop_id, db)

    if drop.status != DropStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail="Drop is not paused"
        )

    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if drop.opens_at <= now < drop.closes_at:
            drop.status = DropStatus.ENTRY_OPEN
        elif now < drop.opens_at:
            drop.status = DropStatus.SCHEDULED
        else:
            drop.status = DropStatus.ENTRY_CLOSED

        await db.commit()
        await db.refresh(drop)
    except Exception:
        await db.rollback()
        raise

    return drop

async def execute_drop_draw(drop: Drop, db: AsyncSession) -> Drop:
    """
    Synchronously executes winner selection and state progression for a closed drop.
    Does not crash if 0 entries exist.
    """
    from datetime import datetime, timezone, timedelta
    from backend.models.entry import Entry
    from backend.models.order import Order
    from backend.models.order_items import OrderItem
    from backend.models.reservations import Reservation
    from backend.enums.order_status import OrderStatus
    from backend.tasks.drop_tasks import expire_unpaid_reservations, _check_and_complete_drop
    import random

    if drop.status in (DropStatus.COMPLETED, DropStatus.CANCELLED):
        return drop

    stmt = select(Entry).where(Entry.drop_id == drop.drop_id)
    entries = (await db.execute(stmt)).scalars().all()

    if not entries:
        if drop.drop_inventory > 0:
            from backend.models.products import Product
            product = (await db.execute(select(Product).where(Product.product_id == drop.product_id))).scalar_one_or_none()
            if product:
                product.stock += drop.drop_inventory
            drop.drop_inventory = 0
        drop.status = DropStatus.COMPLETED
        await db.commit()
        await db.refresh(drop)
        return drop

    unranked = [e for e in entries if e.ranking is None]
    if unranked:
        random.shuffle(entries)
        for rank, entry in enumerate(entries, start=1):
            entry.ranking = rank
        await db.flush()

    reservations_stmt = (
        select(Reservation)
        .join(Entry, Entry.entry_id == Reservation.entry_id)
        .where(Entry.drop_id == drop.drop_id)
    )
    existing_reservations = (await db.execute(reservations_stmt)).scalars().all()

    if not existing_reservations and drop.drop_inventory > 0:
        sorted_entries = sorted(entries, key=lambda e: e.ranking or 999999)
        winners = sorted_entries[:drop.drop_inventory]

        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        for winner in winners:
            order = Order(
                user_id=winner.user_id,
                total_amount=drop.product_price,
                status=OrderStatus.PENDING,
                expires_at=expires_at,
                address=winner.address
            )
            db.add(order)
            await db.flush()

            order_item = OrderItem(
                order_id=order.order_id,
                product_id=drop.product_id,
                quantity=1,
                unit_price=drop.product_price,
                subtotal=drop.product_price,
                size=winner.size
            )
            db.add(order_item)
            drop.drop_inventory -= 1

            reservation = Reservation(
                entry_id=winner.entry_id,
                order_id=order.order_id
            )
            db.add(reservation)
            await db.flush()

            expire_unpaid_reservations.apply_async(
                args=[reservation.reservation_id],
                eta=order.expires_at
            )

        drop.status = DropStatus.CLAIMING

    await _check_and_complete_drop(drop, db)

    await db.commit()
    await db.refresh(drop)
    return drop

async def drop_draw(drop_id: int, db: AsyncSession) -> Drop:
    drop = await get_drop_or_404(drop_id, db)
    return await execute_drop_draw(drop, db)

