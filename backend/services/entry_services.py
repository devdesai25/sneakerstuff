from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.enums.drop_status import DropStatus
from backend.schemas.entry import EntryRequest
from backend.models.users import User
from backend.models.entry import Entry
from backend.helpers.drop_helpers import get_drop_or_404, get_entries_or_404

async def create_entry(
    drop_id: int, 
    address: EntryRequest,
    db: AsyncSession, 
    user: User
) -> dict:  
    from backend.services.turnstile_service import verify_turnstile_token
    is_valid_captcha = await verify_turnstile_token(address.captcha_token)
    if not is_valid_captcha:
        raise HTTPException(
            status_code=400,
            detail="Cloudflare CAPTCHA verification failed. Please complete the CAPTCHA and try again."
        )

    drop = await get_drop_or_404(drop_id, db)

    from datetime import datetime, timezone
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
    
    try:
        entry = (
            await db.execute(
                select(Entry)
                .where(Entry.drop_id == drop_id, Entry.user_id == user.id)
            )
        ).scalar_one_or_none()
        
        if entry:
            raise HTTPException(
                status_code=400,
                detail="You have already entered the drop"
            )
        entry = Entry(
            drop_id = drop_id,
            user_id = user.id,
            address = address.address,
            size = address.size
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail= "You have already entered the drop"
        )
    
    except Exception:
        await db.rollback()
        raise 

    return {
        "message" : "User entered drop successfully"
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
            detail= "User cannot exit from a drop after drop has closed"
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
        "message" : "Entry deleted successfully"
    }

async def check_entry(
    drop_id: int,
    user: User,
    db: AsyncSession,
): 
    drops = await get_drop_or_404(drop_id, db)

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
    except Exception:
        raise
    return entry

async def count_entry(
  drop_id: int,
  db: AsyncSession
):
    drop = await get_drop_or_404(drop_id, db)

    try:
        stmt = (
            select(func.count(Entry.entry_id))
            .select_from(Entry)
            .where(Entry.drop_id == drop_id)
        )

        result = await db.execute(stmt)
        count = result.scalar_one()

    except Exception:
        raise

    return count


from sqlalchemy.orm import selectinload

async def user_entries(
    user: User,
    db: AsyncSession
) -> list[Entry]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    from backend.services.drop_service import execute_drop_draw

    from backend.models.reservations import Reservation
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
            if now >= entry.drop.closes_at and entry.drop.status in (DropStatus.SCHEDULED, DropStatus.ENTRY_OPEN, DropStatus.ENTRY_CLOSED, DropStatus.SELECTING):
                await execute_drop_draw(entry.drop, db)
                needs_refresh = True

    if needs_refresh:
        # Re-fetch entries to reflect newly generated reservations and rankings
        entries = (await db.execute(stmt)).scalars().all()

    for entry in entries:
        if entry.reservation and entry.reservation.order:
            entry.reservation.order_status = entry.reservation.order.status

    return entries
