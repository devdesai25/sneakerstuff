import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.tasks.drop_tasks import (
    _activate_drop, _close_drop, _select_winners, _expire_unpaid_reservations
)
from backend.models.drops import Drop
from backend.models.entry import Entry
from backend.models.order import Order
from backend.models.reservations import Reservation
from backend.models.users import User
from backend.enums.drop_status import DropStatus
from backend.schemas.entry import EntryRequest
from backend.services.entry_services import create_entry

class DummyTask:
    def retry(self, exc=None, countdown=None):
        return exc

@pytest.fixture
def mock_celery_session(db: AsyncSession):
    """Fixture to mock CelerySessionLocal to return the test db session without closing it prematurely."""
    mock_session = AsyncMock()
    mock_session.commit = db.commit
    mock_session.rollback = db.rollback
    mock_session.execute = db.execute
    mock_session.add = db.add
    mock_session.flush = db.flush
    mock_session.close = AsyncMock()
    
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_session
    mock_cm.__aexit__.return_value = None
    return mock_cm

@pytest.mark.asyncio
async def test_activate_drop_success(db: AsyncSession, drop: Drop, mock_celery_session):
    """Test activating a drop."""
    task = DummyTask()
    
    with patch('backend.tasks.drop_tasks.CelerySessionLocal', return_value=mock_celery_session):
        await _activate_drop(task, drop.drop_id)
        
    res = await db.execute(select(Drop).where(Drop.drop_id == drop.drop_id))
    updated_drop = res.scalar_one()
    assert updated_drop.status == DropStatus.ENTRY_OPEN

@pytest.mark.asyncio
async def test_close_drop_success(db: AsyncSession, drop: Drop, user: User, mock_celery_session):
    """Test closing a drop and assigning rankings."""
    task = DummyTask()
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    # Add an entry
    address = EntryRequest(address="123 Test St", captcha_token="valid_token")
    with patch('backend.services.turnstile_service.verify_turnstile_token', return_value=True):
        await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
    
    with patch('backend.tasks.drop_tasks.CelerySessionLocal', return_value=mock_celery_session):
        with patch('backend.tasks.drop_tasks.select_winners.apply_async') as mock_apply:
            await _close_drop(task, drop.drop_id)
            mock_apply.assert_called_once_with(args=[drop.drop_id], countdown=30)
            
    res = await db.execute(select(Drop).where(Drop.drop_id == drop.drop_id))
    updated_drop = res.scalar_one()
    assert updated_drop.status == DropStatus.ENTRY_CLOSED
    
    # Verify rankings assigned
    db_entry = (
        await db.execute(select(Entry).where(Entry.drop_id == drop.drop_id))
    ).scalar_one_or_none()
    
    assert db_entry is not None
    assert db_entry.ranking == 1

@pytest.mark.asyncio
async def test_select_winners_success(db: AsyncSession, drop: Drop, user: User, mock_celery_session):
    """Test selecting winners for a closed drop."""
    task = DummyTask()
    drop.status = DropStatus.ENTRY_OPEN
    drop.drop_inventory = 1
    await db.commit()
    
    # Add entry
    address = EntryRequest(address="123 Test St", captcha_token="valid_token")
    with patch('backend.services.turnstile_service.verify_turnstile_token', return_value=True):
        await create_entry(drop_id=drop.drop_id, address=address, db=db, user=user)
        
    db_entry = (
        await db.execute(select(Entry).where(Entry.drop_id == drop.drop_id))
    ).scalar_one()
    db_entry.ranking = 1
    drop.status = DropStatus.ENTRY_CLOSED
    await db.commit()
    
    with patch('backend.tasks.drop_tasks.CelerySessionLocal', return_value=mock_celery_session):
        with patch('backend.tasks.drop_tasks.expire_unpaid_reservations.apply_async') as mock_apply:
            await _select_winners(task, drop.drop_id)
            mock_apply.assert_called_once()
            
    res = await db.execute(select(Drop).where(Drop.drop_id == drop.drop_id))
    updated_drop = res.scalar_one()
    # Inventory should be reduced by 1
    assert updated_drop.drop_inventory == 0
    # A reservation and order should be created
    reservation = (
        await db.execute(select(Reservation).where(Reservation.entry_id == db_entry.entry_id))
    ).scalar_one_or_none()
    assert reservation is not None
    
    order = (
        await db.execute(select(Order).where(Order.order_id == reservation.order_id))
    ).scalar_one_or_none()
    assert order is not None
    assert order.total_amount == drop.product_price
