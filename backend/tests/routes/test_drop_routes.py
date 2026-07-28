from unittest.mock import patch

import pytest

from datetime import datetime, timezone, timedelta
from backend.enums.drop_status import DropStatus
from backend.tests.factories import create_drop, create_product

@pytest.mark.asyncio
async def test_get_public_drops(
    client,
    db,
    product,
):
    await create_drop(
        db,
        product,
        is_visible=True,
        status=DropStatus.SCHEDULED,
    )

    await create_drop(
        db,
        product,
        is_visible=False,
        status=DropStatus.SCHEDULED
    )

    response = await client.get("/api/drops")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["is_visible"] is True

@pytest.mark.asyncio
async def test_get_all_drops_admin(
    client,
    admin_headers,
):
    
    response = await client.get(
        "/api/admin/drop",
        headers=admin_headers,
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_all_drops_forbidden(
    client,
    user_headers,
):
    
    response = await client.get(
        "/api/admin/drop",
        headers=user_headers,
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_drop_route_success(
    client,
    admin_headers,
    product,
):
    opens_at = datetime.now(timezone.utc) + timedelta(hours=1)
    closes_at = datetime.now(timezone.utc) + timedelta(hours=2)
    
    payload = {
        "product_id": product.product_id,
        "opens_at":  opens_at.isoformat(),
        "closes_at": closes_at.isoformat(),
        "drop_inventory": 5,
        "is_visible": True,
    }

    response = await client.post(
        "/api/admin/drop",
        json=payload,
        headers=admin_headers
        )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_drop_route_forbidden(
    client,
    user_headers,
    product,
):
    opens_at = datetime.now(timezone.utc) + timedelta(hours=1)
    closes_at = datetime.now(timezone.utc) + timedelta(hours=2)
    
    payload = {
        "product_id": product.product_id,
        "opens_at":  opens_at.isoformat(),
        "closes_at": closes_at.isoformat(),
        "drop_inventory": 5,
        "is_visible": True,
    }

    response = await client.post(
        "/api/admin/drop",
        json=payload,
        headers=user_headers
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_drop_route_validation(
    client,
    admin_headers,
):
    
    response = await client.post(
        "/api/admin/drop",
        json={},
        headers=admin_headers
    )

    assert response.status_code == 422
# ======================
# PATCH /api/admin/drop/{id}
# ======================

@pytest.mark.asyncio
async def test_update_drop_route_success(
    client,
    admin_headers,
    drop,
):
    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}",
        json={
            "drop_inventory":3
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    
    assert response.json()["drop_inventory"] == 3

@pytest.mark.asyncio
async def test_update_drop_route_forbidden(
    client,
    user_headers,
    drop
):
    
    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}",
        json={
            "drop_inventory":3
        },
        headers=user_headers
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_drop_route_validation(
    client,
    admin_headers,
    drop
):
    
    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}",
        json={
            "drop_inventory":"abc"
        },
        headers=admin_headers
    )

    assert response.status_code == 422

# =====================
# POST /publish
# =====================

@pytest.mark.asyncio
@patch("backend.services.drop_service.activate_drop.apply_async")
@patch("backend.services.drop_service.close_drop.apply_async")

async def test_publish_drop_route_success(
    mock_close,
    mock_activate,
    client,
    admin_headers,
    drop
):
    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}/publish",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == DropStatus.SCHEDULED

    mock_activate.assert_called_once()
    mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_publish_drop_route_forbidden(
    client,
    user_headers,
    drop
):
    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}/publish",
        headers=user_headers
    )

    assert response.status_code == 403


# =====================
# POST /cancel
# =====================

@pytest.mark.asyncio
async def test_cancel_drop_route_success(
    client,
    admin_headers,
    drop,
):

    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}/cancel",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

@pytest.mark.asyncio
async def test_cancel_drop_route_forbidden(
    client,
    user_headers,
    drop,
):

    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}/cancel",
        headers=user_headers,
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_drop_route_success(
    client,
    admin_headers,
    drop,
):

    response = await client.delete(
        f"/api/admin/drop/{drop.drop_id}/delete",
        headers=admin_headers,
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_drop_route_forbidden(
    client,
    user_headers,
    drop,
):

    response = await client.delete(
        f"/api/admin/drop/{drop.drop_id}/delete",
        headers=user_headers,
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_toggle_visibility_forbidden(
    client,
    user_headers,
    drop,
):

    response = await client.patch(
        f"/api/admin/drop/{drop.drop_id}/toggle-visibility",
        headers=user_headers,
    )

    assert response.status_code == 403
"""
import pytest

from backend.main import app


@pytest.mark.asyncio
async def test_print_routes():

    print("\n========== REGISTERED ROUTES ==========\n")

    for route in app.routes:
        methods = ", ".join(sorted(route.methods))
        print(f"{methods:20} {route.path}")

    print("\n=======================================\n")
    """