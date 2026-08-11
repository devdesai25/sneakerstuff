import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta

from backend.services.drop_service import drop_create, drop_update, drop_publish, drop_cancel, drop_delete
from backend.helpers.drop_helpers import get_drop_or_404
from backend.schemas.drops import DropCreate, DropUpdate
from backend.enums.drop_status import DropStatus

from backend.tests.factories import create_product, create_drop

# ================================================
# drop_create()
# ================================================

@pytest.mark.asyncio
async def test_drop_create_success(db, product):

    payload = DropCreate(
        product_id=product.product_id,
        opens_at=datetime.now(timezone.utc) + timedelta(hours=1),
        closes_at=datetime.now(timezone.utc) + timedelta(hours=2),
        drop_inventory=5,
        is_visible=True
    )

    drop = await drop_create(payload, db)

    assert drop.product_id == product.product_id
    assert drop.product_name == product.name
    assert drop.product_price == product.price
    assert drop.product_image == product.images
    assert drop.drop_inventory == 5
    assert drop.status == DropStatus.DRAFT
    assert drop.is_visible is True

@pytest.mark.asyncio
async def test_drop_create_product_not_found(db):

    payload = DropCreate(
        product_id=99999,
        opens_at=datetime.now(timezone.utc) + timedelta(hours=1),
        closes_at=datetime.now(timezone.utc) + timedelta(hours=2),
        drop_inventory=5,
        is_visible=True,
    )

    with pytest.raises(HTTPException) as exc:

        await drop_create(payload, db)
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"

@pytest.mark.asyncio
async def test_drop_create_insufficient(db, user):

    product = await create_product(
        db,
        stock=2,
        created_by=user.id
    )

    payload = DropCreate(
        product_id=product.product_id,
        opens_at=datetime.now(timezone.utc) + timedelta(hours=1),
        closes_at=datetime.now(timezone.utc) + timedelta(hours=2),
        drop_inventory=5,
        is_visible=True,
    )

    with pytest.raises(HTTPException) as exc:

        await drop_create(payload, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Insufficient stock"

@pytest.mark.asyncio
async def test_drop_create_invalid_dates(db, product):

    now = datetime.now(timezone.utc)

    payload = DropCreate(
        product_id=product.product_id,
        opens_at=now,
        closes_at=now,
        drop_inventory=5,
        is_visible=True,
    )

    with pytest.raises(HTTPException) as exc:

        await drop_create(payload, db)

    assert exc.value.status_code == 422

@pytest.mark.asyncio
async def test_drop_create_integrity_error(db, product):

    payload = DropCreate(
        product_id=product.product_id,
        opens_at=datetime.now(timezone.utc) + timedelta(hours=1),
        closes_at=datetime.now(timezone.utc) + timedelta(hours=2),
        drop_inventory=5,
        is_visible=True,
    )

    with patch.object(
        db,
        "commit",
        AsyncMock(
            side_effect=IntegrityError("","","")
        ),
    ):  
        
        with pytest.raises(HTTPException) as exc:

            await drop_create(payload, db)

    assert exc.value.status_code == 409

# ================================================
# drop_update()
# ================================================

@pytest.mark.asyncio
async def test_drop_update_success(db, product):

    drop = await create_drop(db, product)

    payload = DropUpdate(
        drop_inventory=3,
        is_visible=False,
    )

    updated = await drop_update(
        drop.drop_id, 
        payload,
        db,
    )

    assert updated.drop_inventory == 3
    assert updated.is_visible is False

@pytest.mark.asyncio
async def test_drop_update_not_found(db):

    payload = DropUpdate(
        drop_inventory=5
    )

    with pytest.raises(HTTPException) as exc:
        
        await drop_update(
            99999,
            payload,
            db
        )
    
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_drop_update_non_draft(db, product):

    drop = await create_drop(
        db,
        product,
        status=DropStatus.SCHEDULED,
    )

    payload = DropUpdate(
        drop_inventory=2,
    )

    with pytest.raises(HTTPException) as exc:

        await drop_update(
            drop.drop_id,
            payload,
            db,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid state transition"

@pytest.mark.asyncio
async def test_drop_update_insufficient_stock(db, admin_user):

    product = await create_product(
        db, 
        stock=2,
        created_by=admin_user.id
    )

    drop = await create_drop(
        db,
        product,
        drop_inventory=2
    )

    payload = DropUpdate(
        drop_inventory=5,
    )

    with pytest.raises(HTTPException) as exc:

        await drop_update(
            drop.drop_id,
            payload,
            db
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Insufficient stock"

@pytest.mark.asyncio
async def test_drop_update_invalid_dates(db, product):

    drop = await create_drop(
        db,
        product
    )

    now = datetime.now(timezone.utc)

    payload = DropUpdate(
        opens_at=now,
        closes_at=now
    )

    with pytest.raises(HTTPException) as exc:

        await drop_update(
            drop.drop_id,
            payload,
            db
        )
    
    assert exc.value.status_code == 422
    assert exc.value.detail == "Unprocessable entity"

@pytest.mark.asyncio
async def test_drop_update_integrity_error(db, product):

    drop = await create_drop(
        db,
        product
    )

    payload = DropUpdate(
        drop_inventory=4
    )
    with patch.object(
        db,
        "commit",
        AsyncMock(
            side_effect=IntegrityError("","","")
        ),
    ):
        with pytest.raises(HTTPException) as exc:

            await drop_update(
                drop.drop_id,
                payload,
                db
            )
        
    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"

# ================================================
# drop_publish()
# ================================================

@pytest.mark.asyncio
@patch("backend.services.drop_service.activate_drop.apply_async")
@patch("backend.services.drop_service.close_drop.apply_async")
async def test_drop_publish_success(
    mock_close,
    mock_activate,
    db,
    product,
):
    original_stock = product.stock

    drop = await create_drop(
        db,
        product,
        drop_inventory=5,
    )

    published = await drop_publish(
        drop.drop_id,
        db,
    )

    assert published.status == DropStatus.SCHEDULED
    assert product.stock == original_stock - 5

    mock_activate.assert_called_once_with(
        args=[drop.drop_id],
        eta=drop.opens_at
    )
    mock_close.assert_called_once_with(
        args=[drop.drop_id],
        eta=drop.closes_at
    ) 

@pytest.mark.asyncio
async def test_drop_publish_not_found(db):

    with pytest.raises(HTTPException) as exc:

        await drop_publish(
            999999,
            db
        )
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Drop not found"

@pytest.mark.asyncio
async def test_drop_publish_invalid_state(db, product):
    
    drop = await create_drop(
        db,
        product,
        status=DropStatus.CANCELLED
    )

    with pytest.raises(HTTPException) as exc:

        await drop_publish(
            drop.drop_id,
            db
        )
    
    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid state transition"

@pytest.mark.asyncio
async def test_drop_publish_negative_inventory(db, product):
    
    drop = await create_drop(
        db,
        product,
        drop_inventory = -1,
    )

    with pytest.raises(HTTPException) as exc:

        await drop_publish(
            drop.drop_id,
            db
        )
    
    assert exc.value.status_code == 422
    assert exc.value.detail == "Drop inventory cannot be zero or less than zero"

@pytest.mark.asyncio
async def test_drop_publish_insufficient_stock(db, admin_user):

    product = await create_product(
        db,
        stock=2,
        created_by=admin_user.id
    )

    drop = await create_drop(
        db,
        product,
        drop_inventory=5
    )

    with pytest.raises(HTTPException) as exc:

        await drop_publish(
            drop.drop_id,
            db
        )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Insufficient stock"

@pytest.mark.asyncio
async def test_drop_publish_integrity_error(db, product):
    
    drop = await create_drop(
        db,
        product
    )

    with patch.object(
        db,
        "commit",
        AsyncMock(
            side_effect=IntegrityError("","","")
        )
    ):
        
        with pytest.raises(HTTPException) as exc:

            await drop_publish(
                drop.drop_id,
                db,
            )
    
    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"

# ================================================
# drop_cancel()
# ================================================

@pytest.mark.asyncio
async def test_drop_cancel_success(db, product):

    drop = await create_drop(
        db, 
        product,
        drop_inventory=5,
    )

    original_stock = product.stock

    cancelled = await drop_cancel(
        drop.drop_id,
        db
    )

    assert cancelled.status == DropStatus.CANCELLED
    assert cancelled.drop_inventory == 5

@pytest.mark.asyncio
async def test_drop_cancel_stock_restore_success(db, product):

    drop = await create_drop(
        db,
        product,
        drop_inventory=5
    )

    original_stock = product.stock - 5 

    cancelled = await drop_cancel(
            drop.drop_id,
            db
        )
    
    assert cancelled.status == DropStatus.CANCELLED
    assert cancelled.drop_inventory == drop.drop_inventory
    assert product.stock == original_stock + 5

@pytest.mark.asyncio
async def test_drop_cancel_not_found(db):

    with pytest.raises(HTTPException) as exc:

        await drop_cancel(
            99999,
            db
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Drop not found"

@pytest.mark.asyncio
async def test_drop_cancel_invalid_state(db, product):

    drop = await create_drop(
        db,
        product,
        status=DropStatus.CLAIMING
    )

    with pytest.raises(HTTPException) as exc:

        await drop_cancel(
            drop.drop_id,
            db
        )
    
    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid state transition"

@pytest.mark.asyncio
async def test_drop_cancel_integrity_error(db, product):

    drop = await create_drop(
        db,
        product,
    )

    with patch.object(
        db,
        "commit",
        AsyncMock(
            side_effect=IntegrityError("","","")
        ),
    ):
        with pytest.raises(HTTPException) as exc:

            await drop_cancel(
                drop.drop_id,
                db
            )
    
    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"

# ================================================
# drop_delete()
# ================================================

@pytest.mark.asyncio
async def test_drop_delete_success(db, product):

    drop = await create_drop(
        db,
        product,
        drop_inventory=5,
    )

    original_stock = product.stock

    await drop_delete(
        drop.drop_id,
        db
    )

    with pytest.raises(HTTPException):
        await get_drop_or_404(
            drop.drop_id,
            db,
        )
    
    assert product.stock == original_stock 

@pytest.mark.asyncio
async def test_drop_delete_not_found(db):

    with pytest.raises(HTTPException) as exc:

        await drop_delete(
            99999,
            db
        )
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Drop not found"

@pytest.mark.asyncio
async def test_drop_delete_invalid_state(db, product):

    payload = await create_drop(
        db,
        product,
        status=DropStatus.ENTRY_OPEN
    )

    with pytest.raises(HTTPException) as exc:

        await drop_delete(
            payload.drop_id,
            db
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid state transition"

@pytest.mark.asyncio
async def test_drop_delete_integrity_error(db, product):

    drop = await create_drop(db, product)

    with patch.object(
        db,
        "commit",
        AsyncMock(
            side_effect=IntegrityError("","","")
        ),
    ):
        with pytest.raises(HTTPException) as exc:

            await drop_delete(
                drop.drop_id,
                db
            )
    
    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"


@pytest.mark.asyncio
async def test_execute_drop_draw_10_min_window_and_concurrency(db, product, user):
    from backend.services.drop_service import execute_drop_draw
    from backend.models.entry import Entry
    from backend.models.reservations import Reservation
    from datetime import datetime, timezone, timedelta

    drop = await create_drop(
        db,
        product,
        drop_inventory=1,
        status=DropStatus.ENTRY_CLOSED,
        opens_at=datetime.now(timezone.utc) - timedelta(hours=2),
        closes_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    entry = Entry(drop_id=drop.drop_id, user_id=user.id, address="Test Addr 1")
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    # First draw call
    drawn_drop = await execute_drop_draw(drop, db)
    assert drawn_drop.status == DropStatus.CLAIMING

    res_stmt = select(Reservation).join(Entry).where(Entry.drop_id == drop.drop_id)
    res = (await db.execute(res_stmt)).scalar_one()
    expires_at = res.order.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    diff = expires_at - datetime.now(timezone.utc)
    # Expiration should be roughly 10 minutes
    assert 540 <= diff.total_seconds() <= 620

    # Second draw call (simulating concurrent trigger)
    drawn_again = await execute_drop_draw(drop, db)
    assert drawn_again.status == DropStatus.CLAIMING
    all_res = (await db.execute(res_stmt)).scalars().all()
    assert len(all_res) == 1