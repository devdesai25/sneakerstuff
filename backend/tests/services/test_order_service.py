import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.enums.order_status import OrderStatus
from backend.models.cart_items import CartItem
from backend.models.order import Order
from backend.models.order_items import OrderItem
from backend.models.products import Product
from backend.schemas.orders import OrderRequest
from backend.services.order_service import (
    order_get,
    order_create,
    order_pay,
    order_cancel,
)


@pytest.mark.asyncio
async def test_order_get_success(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Test Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    result = await order_get(user, db)

    assert len(result) == 1
    assert result[0].order_id == order.order_id
    assert result[0].user_id == user.id
    assert result[0].status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_order_get_not_found_raises_404(db, user):
    with pytest.raises(HTTPException) as exc:
        await order_get(user, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Orders not found"


@pytest.mark.asyncio
async def test_order_create_success(db, user):
    product = Product(
        name="Nike Dunk Low Panda",
        description="Test Product",
        price=Decimal("120.00"),
        stock=10,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    cart_item = CartItem(
        user_id=user.id,
        product_id=product.product_id,
        quantity=2,
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)

    payload = OrderRequest(address="123 Test Street")

    result = await order_create(payload, user, db)

    assert result.order_id is not None
    assert result.user_id == user.id
    assert result.status == OrderStatus.PENDING
    assert result.address == "123 Test Street"
    assert result.total_amount == Decimal("240.00")
    assert result.expires_at > datetime.now(timezone.utc)

    await db.refresh(product)
    assert product.stock == 8

    order_items = (
        await db.execute(
            OrderItem.__table__.select().where(OrderItem.order_id == result.order_id)
        )
    ).all()

    assert len(order_items) == 1
    row = order_items[0]
    assert row.product_id == product.product_id
    assert row.quantity == 2
    assert row.unit_price == Decimal("120.00")
    assert row.subtotal == Decimal("240.00")


@pytest.mark.asyncio
async def test_order_create_cart_not_found_raises_404(db, user):
    payload = OrderRequest(address="123 Test Street")

    with pytest.raises(HTTPException) as exc:
        await order_create(payload, user, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Cart not found"


@pytest.mark.asyncio
async def test_order_create_product_not_found_raises_404(db, user):
    from backend.tests.factories import create_product
    prod = await create_product(db)
    cart_item = CartItem(
        user_id=user.id,
        product_id=prod.product_id,
        quantity=1,
        size="US 9"
    )
    db.add(cart_item)
    await db.commit()

    payload = OrderRequest(address="123 Test Street")

    with patch.object(db, "execute") as mock_exec:
        mock_cart = MagicMock()
        mock_cart.scalars.return_value.all.return_value = [cart_item]
        mock_prod = MagicMock()
        mock_prod.scalar_one_or_none.return_value = None
        mock_exec.side_effect = [mock_cart, mock_prod]

        with pytest.raises(HTTPException) as exc:
            await order_create(payload, user, db)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Product not found"


@pytest.mark.asyncio
async def test_order_create_insufficient_stock_raises_422(db, user):
    product = Product(
        name="Nike Dunk Low Panda",
        description="Test Product",
        price=Decimal("120.00"),
        stock=1,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    cart_item = CartItem(
        user_id=user.id,
        product_id=product.product_id,
        quantity=2,
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)

    payload = OrderRequest(address="123 Test Street")

    with pytest.raises(HTTPException) as exc:
        await order_create(payload, user, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Insufficient stock"

    await db.refresh(product)
    assert product.stock == 1


@pytest.mark.asyncio
async def test_order_create_integrity_error_raises_409(db, user):
    product = Product(
        name="Nike Dunk Low Panda",
        description="Test Product",
        price=Decimal("120.00"),
        stock=10,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    cart_item = CartItem(
        user_id=user.id,
        product_id=product.product_id,
        quantity=1,
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)

    payload = OrderRequest(address="123 Test Street")

    with patch.object(
        db,
        "commit",
        AsyncMock(side_effect=IntegrityError("", "", "")),
    ):
        with pytest.raises(HTTPException) as exc:
            await order_create(payload, user, db)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"


@pytest.mark.asyncio
async def test_order_create_unknown_exception_rolls_back(db, user):
    product = Product(
        name="Nike Dunk Low Panda",
        description="Test Product",
        price=Decimal("120.00"),
        stock=10,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    cart_item = CartItem(
        user_id=user.id,
        product_id=product.product_id,
        quantity=1,
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)

    payload = OrderRequest(address="123 Test Street")

    with patch.object(db, "commit", AsyncMock(side_effect=Exception("boom"))):
        with pytest.raises(Exception):
            await order_create(payload, user, db)


@pytest.mark.asyncio
async def test_order_create_multiple_cart_items_success(db, user):
    product1 = Product(
        name="Nike One",
        description="Test Product 1",
        price=Decimal("100.00"),
        stock=10,
        images="https://example.com/1.jpg",
        created_by=user.id,
    )
    product2 = Product(
        name="Nike Two",
        description="Test Product 2",
        price=Decimal("50.00"),
        stock=20,
        images="https://example.com/2.jpg",
        created_by=user.id,
    )
    db.add_all([product1, product2])
    await db.commit()
    await db.refresh(product1)
    await db.refresh(product2)

    db.add_all(
        [
            CartItem(user_id=user.id, product_id=product1.product_id, quantity=2),
            CartItem(user_id=user.id, product_id=product2.product_id, quantity=4),
        ]
    )
    await db.commit()

    payload = OrderRequest(address="Multi Item Address")

    result = await order_create(payload, user, db)

    assert result.total_amount == Decimal("400.00")

    await db.refresh(product1)
    await db.refresh(product2)
    assert product1.stock == 8
    assert product2.stock == 16


@pytest.mark.asyncio
async def test_order_create_boundary_equal_stock_succeeds(db, user):
    product = Product(
        name="Boundary Shoe",
        description="Test Product",
        price=Decimal("75.00"),
        stock=2,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    cart_item = CartItem(
        user_id=user.id,
        product_id=product.product_id,
        quantity=2,
    )
    db.add(cart_item)
    await db.commit()

    payload = OrderRequest(address="Boundary Address")

    result = await order_create(payload, user, db)

    assert result.total_amount == Decimal("150.00")
    await db.refresh(product)
    assert product.stock == 0


@pytest.mark.asyncio
async def test_order_pay_success(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Pay Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    result = await order_pay(order.order_id, user, db)

    assert result.order_id == order.order_id
    assert result.status == OrderStatus.PAID
    assert result.paid_at is not None


@pytest.mark.asyncio
async def test_order_pay_expired_pending_order_raises_400(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        address="Expired Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_pay(order.order_id, user, db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order has expired"


@pytest.mark.asyncio
async def test_order_pay_already_expired_raises_400(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.EXPIRED,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        address="Expired Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_pay(order.order_id, user, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unprocessable entity"


@pytest.mark.asyncio
async def test_order_pay_expired_raffle_order_raises_422_not_resurrected(db, user, product):
    from backend.models.entry import Entry
    from backend.models.reservations import Reservation
    from backend.models.drops import Drop
    from backend.enums.drop_status import DropStatus

    drop = Drop(
        product_id=product.product_id,
        opens_at=datetime.now(timezone.utc) - timedelta(hours=2),
        closes_at=datetime.now(timezone.utc) - timedelta(hours=1),
        drop_inventory=1,
        product_name="Raffle Shoe",
        product_price=Decimal("150.00"),
        status=DropStatus.CLAIMING
    )
    db.add(drop)
    await db.commit()
    await db.refresh(drop)

    entry = Entry(drop_id=drop.drop_id, user_id=user.id, address="Raffle Addr")
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    order = Order(
        user_id=user.id,
        total_amount=Decimal("150.00"),
        status=OrderStatus.EXPIRED,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        address="Raffle Addr"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    res = Reservation(entry_id=entry.entry_id, order_id=order.order_id)
    db.add(res)
    await db.commit()

    with pytest.raises(HTTPException) as exc:
        await order_pay(order.order_id, user, db)

    assert exc.value.status_code == 422
    assert order.status == OrderStatus.EXPIRED


@pytest.mark.asyncio
async def test_order_pay_cancelled_order_raises_422(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.CANCELLED,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Cancelled Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_pay(order.order_id, user, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unprocessable entity"


@pytest.mark.asyncio
async def test_order_pay_paid_order_raises_422(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PAID,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Paid Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_pay(order.order_id, user, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unprocessable entity"


@pytest.mark.asyncio
async def test_order_pay_integrity_error_raises_409(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Integrity Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with patch.object(
        db,
        "commit",
        AsyncMock(side_effect=IntegrityError("", "", "")),
    ):
        with pytest.raises(HTTPException) as exc:
            await order_pay(order.order_id, user, db)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"


@pytest.mark.asyncio
async def test_order_pay_unknown_exception_rolls_back(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Boom Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with patch.object(db, "commit", AsyncMock(side_effect=Exception("boom"))):
        with pytest.raises(Exception):
            await order_pay(order.order_id, user, db)


@pytest.mark.asyncio
async def test_order_cancel_success_restores_stock(db, user):
    product = Product(
        name="Cancel Shoe",
        description="Test Product",
        price=Decimal("90.00"),
        stock=3,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    order = Order(
        user_id=user.id,
        total_amount=Decimal("180.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Cancel Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    order_item = OrderItem(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=2,
        unit_price=Decimal("90.00"),
        subtotal=Decimal("180.00"),
    )
    db.add(order_item)
    await db.commit()
    await db.refresh(order_item)

    result = await order_cancel(order.order_id, user, db)

    assert result.status == OrderStatus.CANCELLED

    await db.refresh(product)
    assert product.stock == 5


@pytest.mark.asyncio
async def test_order_cancel_expired_order_raises_400(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.EXPIRED,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        address="Expired Cancel Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_cancel(order.order_id, user, db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order has Expired"


@pytest.mark.asyncio
async def test_order_cancel_pending_order_not_found_raises_404(db, user):
    with pytest.raises(HTTPException) as exc:
        await order_cancel(99999, user, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Order not found"


@pytest.mark.asyncio
async def test_order_cancel_paid_order_raises_422(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PAID,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Paid Cancel Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_cancel(order.order_id, user, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unprocessable entity"


@pytest.mark.asyncio
async def test_order_cancel_cancelled_order_raises_422(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.CANCELLED,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Cancelled Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with pytest.raises(HTTPException) as exc:
        await order_cancel(order.order_id, user, db)

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unprocessable entity"


@pytest.mark.asyncio
async def test_order_cancel_expired_pending_order_raises_400(db, user):
    product = Product(
        name="Expired Cancel Shoe",
        description="Test Product",
        price=Decimal("90.00"),
        stock=3,
        images="https://example.com/image.jpg",
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    order = Order(
        user_id=user.id,
        total_amount=Decimal("180.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        address="Expired Pending Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    order_item = OrderItem(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=2,
        unit_price=Decimal("90.00"),
        subtotal=Decimal("180.00"),
    )
    db.add(order_item)
    await db.commit()
    await db.refresh(order_item)

    with pytest.raises(HTTPException) as exc:
        await order_cancel(order.order_id, user, db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order has expired"

    await db.refresh(product)
    assert product.stock == 5


@pytest.mark.asyncio
async def test_order_cancel_integrity_error_raises_409(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Integrity Cancel Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with patch.object(
        db,
        "commit",
        AsyncMock(side_effect=IntegrityError("", "", "")),
    ):
        with pytest.raises(HTTPException) as exc:
            await order_cancel(order.order_id, user, db)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Database integrity error"


@pytest.mark.asyncio
async def test_order_cancel_unknown_exception_rolls_back(db, user):
    order = Order(
        user_id=user.id,
        total_amount=Decimal("100.00"),
        status=OrderStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        address="Boom Cancel Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    with patch.object(db, "commit", AsyncMock(side_effect=Exception("boom"))):
        with pytest.raises(Exception):
            await order_cancel(order.order_id, user, db)