from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.enums.drop_status import DropStatus
from backend.models.drops import Drop
from backend.models.entry import Entry


async def drop_get(db: AsyncSession) -> list[Drop]:
    drops = (
        await db.execute(
            select(Drop)
        )
    ).scalars().all()

    now = datetime.now(timezone.utc)
    updated = False
    for drop in drops:
        if drop.status in (DropStatus.SCHEDULED, DropStatus.ENTRY_OPEN) and now >= drop.closes_at:
            drop.status = DropStatus.ENTRY_CLOSED
            updated = True

    if updated:
        await db.commit()
    
    return drops


async def get_drop_or_404(drop_id: int, db: AsyncSession) -> Drop:
    drop = (
        await db.execute(
            select(Drop).where(Drop.drop_id == drop_id)
        )
    ).scalar_one_or_none()

    if not drop:
        raise HTTPException(
            status_code=404,
            detail="Drop not found"
        )

    return drop


async def get_entries_or_404(drop_id: int, db: AsyncSession) -> list[Entry]:
    entries = (
        await db.execute(
            select(Entry)
            .where(Entry.drop_id == drop_id)
        )
    ).scalars().all()

    if not entries:
        raise HTTPException(
            status_code=404,
            detail="Entries not found"
        )
    
    return entries
