from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.users import User
from backend.schemas.entry import EntryRequest, EntryResponse
from backend.services.auth import get_current_user
from backend.services.entry_services import (
    check_entry,
    count_entry,
    create_entry,
    delete_entry,
    user_entries,
)

router = APIRouter(tags=["Entry"])


@router.post("/drops/{drop_id}/entries")
async def entry_create(
    drop_id: int,
    address: EntryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return await create_entry(drop_id, address, db, user)


@router.delete("/drops/{drop_id}/entries")
async def entry_delete(
    drop_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return await delete_entry(drop_id, db, user)


@router.get("/drops/{drop_id}/entries/me")
async def entry_me(
    drop_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await check_entry(drop_id, user, db)


@router.get("/drops/{drop_id}/entries/count")
async def entry_count(
    drop_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await count_entry(drop_id, db)


@router.get("/users/me/entries", response_model=list[EntryResponse])
async def get_drop_user(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await user_entries(user, db)
