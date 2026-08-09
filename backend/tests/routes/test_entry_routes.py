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
        json={"address": "Route Address 123"},
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "User entered drop successfully"}

@pytest.mark.asyncio
async def test_create_entry_route_closed(client: AsyncClient, user_headers: dict, drop: Drop):
    """Test creating an entry when drop is not open via route."""
    response = await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123"},
        headers=user_headers
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Entries are not open for this drop"

@pytest.mark.asyncio
async def test_delete_entry_route(client: AsyncClient, user_headers: dict, drop: Drop, db: AsyncSession):
    """Test deleting an entry via route."""
    drop.status = DropStatus.ENTRY_OPEN
    await db.commit()
    
    await client.post(
        f"/api/drops/{drop.drop_id}/entries",
        json={"address": "Route Address 123"},
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
        json={"address": "Route Address 123"},
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
        json={"address": "Route Address 123"},
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
        json={"address": "Route Address 123"},
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
