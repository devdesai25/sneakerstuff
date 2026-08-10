import pytest
from httpx import AsyncClient
from backend.models.drops import Drop
from backend.enums.drop_status import DropStatus
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_entry_route(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test creating an entry for a drop via route."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    response = await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": "1x0000000000000000000000000000000AA"},
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "User entered drop successfully"}

@pytest.mark.asyncio
async def test_create_entry_route_closed(client: AsyncClient, user_headers: dict, drop: Drop):
    """Test creating an entry when drop is not open via route."""
    response = await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": "1x0000000000000000000000000000000AA"},
        headers=user_headers
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Drop drawing has not opened yet."

@pytest.mark.asyncio
async def test_delete_entry_route(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test deleting an entry via route."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": "1x0000000000000000000000000000000AA"},
        headers=user_headers
    )
    
    response = await client.delete(
        f"/api/drops/{drop.drop_id}/entries",
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Entry deleted successfully"}

@pytest.mark.asyncio
async def test_check_entry_me_route(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test checking user's own entry via route."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": "1x0000000000000000000000000000000AA"},
        headers=user_headers
    )
    
    response = await client.get(
        f"/api/drops/{drop.drop_id}/entries/me",
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json()["drop_id"] == drop.drop_id
    assert response.json()["address"] == "Route Address 123"

@pytest.mark.asyncio
async def test_count_entries_route(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test getting entry count for a drop via route."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": "1x0000000000000000000000000000000AA"},
        headers=user_headers
    )
    
    response = await client.get(f"/api/drops/{drop.drop_id}/entries/count")
    
    assert response.status_code == 200
    assert response.json() == 1

@pytest.mark.asyncio
async def test_get_user_entries_route(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test getting all entries for the authenticated user via route."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": "1x0000000000000000000000000000000AA"},
        headers=user_headers
    )
    
    response = await client.get(
        "/api/users/me/entries",
        headers=user_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["drop_id"] == drop.drop_id

@pytest.mark.asyncio
async def test_create_entry_route_invalid_captcha(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test creating an entry with invalid or missing captcha token fails."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    response = await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123", "captcha_token": ""},
        headers=user_headers
    )
    
    assert response.status_code == 400
    assert "CAPTCHA verification failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_entry_duplicate_device_fingerprint(client: AsyncClient, user_headers: dict, admin_headers: dict, drop: Drop, db: AsyncSession):
    """Test that two different users submitting from the same device fingerprint are rejected."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()

    # User 1 submits entry with device fingerprint
    res1 = await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={
            "address": "Device Test Address 1",
            "captcha_token": "1x0000000000000000000000000000000AA",
            "device_fingerprint": "test_device_hash_12345"
        },
        headers=user_headers
    )
    assert res1.status_code == 200

    # User 2 attempts to submit entry with the exact same device fingerprint
    res2 = await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={
            "address": "Device Test Address 2",
            "captcha_token": "1x0000000000000000000000000000000AA",
            "device_fingerprint": "test_device_hash_12345"
        },
        headers=admin_headers
    )
    assert res2.status_code == 400
    assert "This device has already been used" in res2.json()["detail"]


