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
    drop = await get_drop_or_404(drop_id, db)

    if drop.status != DropStatus.ENTRY_OPEN:
        raise HTTPException(
            status_code=400,
            detail="Entries are not open for this drop"
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
            address = address.address
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


async def user_entries(
    user: User,
    db: AsyncSession
) -> Entry:
    try: 
        entries = (
            await db.execute(
                select(Entry)
                .where(Entry.user_id == user.id)
            )
        ).scalars().all()

        if not entries:
            raise HTTPException(
                detail="No entries found"
            )
    except Exception:
        raise
    
    return entries
