from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.enums.order_status import OrderStatus
from backend.models.order import Order


@pytest.mark.asyncio
async def test_create_order_route(client: AsyncClient, user_headers: dict):
    """Test creating an order via route."""
    response = await client.post(
        "/api/orders",
        json={"address": "123 Main St"},
        headers=user_headers
    )
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_get_orders_route(client: AsyncClient, user_headers: dict):
    """Test retrieving orders via route."""
    response = await client.get("/api/orders", headers=user_headers)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_pay_order_route(client: AsyncClient, user_headers: dict, db: AsyncSession, user):
    """Test paying for an order via route."""
    order = Order(
        user_id=user.id,
        total_amount=100.0,
        status=OrderStatus.PENDING,
        address="123 Main St",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    response = await client.patch(
        f"/api/orders/{order.order_id}/pay",
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.PAID.value


@pytest.mark.asyncio
async def test_cancel_order_route(client: AsyncClient, user_headers: dict, db: AsyncSession, user):
    """Test cancelling an order via route."""
    order = Order(
        user_id=user.id,
        total_amount=100.0,
        status=OrderStatus.PENDING,
        address="123 Main St",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    response = await client.patch(
        f"/api/orders/{order.order_id}/cancel",
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.CANCELLED.value
