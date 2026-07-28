import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch

from backend.services.entry_services import (
    create_entry, delete_entry, check_entry, count_entry, user_entries
)
from backend.schemas.entry import EntryRequest
from backend.enums.drop_status import DropStatus
from backend.models.users import User
from backend.models.drops import Drop
from backend.models.entry import Entry

@pytest.mark.asyncio
async def test_create_entry_success(db: AsyncSession, user: User, drop: Drop):
    """Test successful creation of a drop entry."""
    # Set drop status to ENTRY_OPEN
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    address = EntryRequest(address="123 Test St")
    
    result = await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    assert result == {"message": "User entered drop successfully"}
    
    db_entry = (
        await db.execute(select(Entry).where(Entry.drop_id == drop.drop_id, Entry.user_id == user.id))
    ).scalar_one_or_none()
    
    assert db_entry is not None
    assert db_entry.address == "123 Test St"

@pytest.mark.asyncio
async def test_create_entry_drop_closed(db: AsyncSession, user: User, drop: Drop):
    """Test entering a drop that is not open for entries."""
    # Default status in factory is DRAFT
    address = EntryRequest(address="123 Test St")
    
    with pytest.raises(HTTPException) as exc_info:
        await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
        
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Entries are not open for this drop"

@pytest.mark.asyncio
async def test_create_entry_duplicate(db: AsyncSession, user: User, drop: Drop):
    """Test entering a drop twice."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    address = EntryRequest(address="123 Test St")
    await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    with pytest.raises(HTTPException) as exc_info:
        await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
        
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "You have already entered the drop"

@pytest.mark.asyncio
async def test_delete_entry_success(db: AsyncSession, user: User, drop: Drop):
    """Test successfully removing an entry from a drop."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    address = EntryRequest(address="123 Test St")
    await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    result = await delete_entry(drop_id=drop.drop_id, db=db, user=user)
    
    assert result == {"message": "Entry deleted successfully"}
    
    db_entry = (
        await db.execute(select(Entry).where(Entry.drop_id == drop.drop_id, Entry.user_id == user.id))
    ).scalar_one_or_none()
    
    assert db_entry is None

@pytest.mark.asyncio
async def test_delete_entry_drop_closed(db: AsyncSession, user: User, drop: Drop):
    """Test removing entry when drop is closed."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    address = EntryRequest(address="123 Test St")
    await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    # Change status to something else
    drop.status = DropStatus.CLOSED
    await db.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        await delete_entry(drop_id=drop.drop_id, db=db, user=user)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User cannot exit from a drop after drop has closed"

@pytest.mark.asyncio
async def test_delete_entry_not_found(db: AsyncSession, user: User, drop: Drop):
    """Test removing non-existent entry."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        await delete_entry(drop_id=drop.drop_id, db=db, user=user)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Entry not found"

@pytest.mark.asyncio
async def test_check_entry_success(db: AsyncSession, user: User, drop: Drop):
    """Test checking an existing entry."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    address = EntryRequest(address="123 Test St")
    await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    entry = await check_entry(drop_id=drop.drop_id, user=user, db=db)
    
    assert entry is not None
    assert entry.drop_id == drop.drop_id
    assert entry.user_id == user.id

@pytest.mark.asyncio
async def test_check_entry_not_found(db: AsyncSession, user: User, drop: Drop):
    """Test checking a non-existent entry."""
    with pytest.raises(HTTPException) as exc_info:
        await check_entry(drop_id=drop.drop_id, user=user, db=db)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Entry not found"

@pytest.mark.asyncio
async def test_count_entry_success(db: AsyncSession, user: User, drop: Drop, admin_user: User):
    """Test counting entries for a drop."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    # Enter user 1
    address1 = EntryRequest(address="123 Test St")
    await create_entry(drop_id=drop.drop_id, address=address1, db=db, user=user)
    
    # Enter user 2
    address2 = EntryRequest(address="456 Test Ave")
    await create_entry(drop_id=drop.drop_id, address=address2, db=db, user=admin_user)
    
    count = await count_entry(drop_id=drop.drop_id, db=db)
    assert count == 2

@pytest.mark.asyncio
async def test_user_entries_success(db: AsyncSession, user: User, drop: Drop):
    """Test getting all entries for a user."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    address = EntryRequest(address="123 Test St")
    await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    entries = await user_entries(user=user, db=db)
    
    assert len(entries) == 1
    assert entries[0].drop_id == drop.drop_id

@pytest.mark.asyncio
async def test_user_entries_not_found(db: AsyncSession, user: User):
    """Test getting entries for a user with no entries."""
    with pytest.raises(HTTPException) as exc_info:
        await user_entries(user=user, db=db)
        
    # The HTTP exception in original code has no status code specified, defaulting to 500, detail="No entries found"
    assert exc_info.value.detail == "No entries found"
