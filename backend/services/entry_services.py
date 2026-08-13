from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.enums.drop_status import DropStatus
from backend.helpers.drop_helpers import get_drop_or_404
from backend.models.entry import Entry
from backend.models.reservations import Reservation
from backend.models.users import User
from backend.schemas.entry import EntryRequest
from backend.services.drop_service import execute_drop_draw
from backend.services.turnstile_service import verify_turnstile_token
from backend.services.websocket_manager import manager


async def create_entry(
    drop_id: int, 
    address: EntryRequest,
    db: AsyncSession, 
    user: User
) -> dict:  
    is_valid_captcha = await verify_turnstile_token(address.captcha_token)
    if not is_valid_captcha:
        raise HTTPException(
            status_code=400,
            detail="Cloudflare CAPTCHA verification failed. Please complete the CAPTCHA and try again."
        )

    drop = await get_drop_or_404(drop_id, db)
    now = datetime.now(timezone.utc)

    # Auto-activate drop status to ENTRY_OPEN if time has passed opens_at and drop is SCHEDULED
    if drop.status == DropStatus.SCHEDULED and drop.opens_at <= now < drop.closes_at:
        drop.status = DropStatus.ENTRY_OPEN
        await db.commit()
        await db.refresh(drop)

    if drop.status != DropStatus.ENTRY_OPEN:
        if now < drop.opens_at:
            raise HTTPException(
                status_code=400,
                detail="Drop drawing has not opened yet."
            )
        elif now >= drop.closes_at:
            raise HTTPException(
                status_code=400,
                detail="Drop drawing is already closed."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Entries are not open for this drop."
            )
    
    # Combined single query for user entry collision or device fingerprint collision
    conditions = [Entry.user_id == user.id]
    if address.device_fingerprint:
        conditions.append(Entry.device_fingerprint == address.device_fingerprint)

    stmt = select(Entry).where(Entry.drop_id == drop_id, or_(*conditions))
    existing_entry = (await db.execute(stmt)).scalars().first()

    if existing_entry:
        if existing_entry.user_id == user.id:
            raise HTTPException(
                status_code=400,
                detail="You have already entered the drop"
            )
        if address.device_fingerprint and existing_entry.device_fingerprint == address.device_fingerprint:
            raise HTTPException(
                status_code=400,
                detail="This device has already been used to register an entry for this drop."
            )

    try:
        entry = Entry(
            drop_id=drop_id,
            user_id=user.id,
            address=address.address,
            size=address.size,
            device_fingerprint=address.device_fingerprint
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)

        await manager.broadcast_to_drop(drop_id, {
            "event": "entry_updated",
            "drop_id": drop_id,
            "action": "created"
        })
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="You have already entered the drop"
        )
    except Exception:
        await db.rollback()
        raise 

    return {
        "message": "User entered drop successfully"
    }


async def delete_entry(
    drop_id: int, 
    db: AsyncSession, 
    user: User
) -> dict:
    drop = await get_drop_or_404(drop_id, db)

    if drop.status != DropStatus.ENTRY_OPEN:
        raise HTTPException(
            status_code=409,
            detail="User cannot exit from a drop after drop has closed"
        )
    
    try:
        entry = (
            await db.execute(
                select(Entry)
                .where(Entry.drop_id == drop_id, Entry.user_id == user.id)
            )
        ).scalar_one_or_none()

        if not entry:
            raise HTTPException(
                status_code=404,
                detail="Entry not found"
            )
        
        await db.delete(entry)
        await db.commit()

        await manager.broadcast_to_drop(drop_id, {
            "event": "entry_updated",
            "drop_id": drop_id,
            "action": "deleted"
        })

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )
    except Exception:
        await db.rollback()
        raise
    
    return {
        "message": "Entry deleted successfully"
    }


async def check_entry(
    drop_id: int,
    user: User,
    db: AsyncSession,
) -> Entry: 
    await get_drop_or_404(drop_id, db)

    entry = (
        await db.execute(
            select(Entry)
            .where(Entry.drop_id == drop_id, Entry.user_id == user.id)
        )
    ).scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Entry not found"
        )

    return entry


async def count_entry(
    drop_id: int,
    db: AsyncSession
) -> int:
    await get_drop_or_404(drop_id, db)

    stmt = (
        select(func.count(Entry.entry_id))
        .select_from(Entry)
        .where(Entry.drop_id == drop_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def user_entries(
    user: User,
    db: AsyncSession
) -> list[Entry]:
    now = datetime.now(timezone.utc)

    stmt = (
        select(Entry)
        .where(Entry.user_id == user.id)
        .options(
            selectinload(Entry.reservation).selectinload(Reservation.order),
            selectinload(Entry.drop)
        )
    )
    entries = (await db.execute(stmt)).scalars().all()

    # If any drop entered by the user has passed closes_at but hasn't drawn winners yet, execute draw!
    needs_refresh = False
    for entry in entries:
        if entry.drop:
            if now >= entry.drop.closes_at and entry.drop.status in (
                DropStatus.SCHEDULED,
                DropStatus.ENTRY_OPEN,
                DropStatus.ENTRY_CLOSED,
                DropStatus.SELECTING,
            ):
                await execute_drop_draw(entry.drop, db)
                needs_refresh = True

    if needs_refresh:
        # Re-fetch entries to reflect newly generated reservations and rankings
        entries = (await db.execute(stmt)).scalars().all()

    for entry in entries:
        if entry.reservation and entry.reservation.order:
            entry.reservation.order_status = entry.reservation.order.status

    return entries
