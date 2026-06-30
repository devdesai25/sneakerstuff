from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.drops import Drop

async def drop_get(db: AsyncSession) -> list[Drop]:

    drop = (
        await db.execute(
            select(Drop)
        )
    ).scalars().all()
    
    return drop

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
