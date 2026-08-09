import pytest
from httpx import AsyncClient
from backend.models.users import User

@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, user_headers: dict, user: User):
    """Test getting current user profile."""
    response = await client.get("/api/me", headers=user_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email

@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """Test getting profile without authentication."""
    response = await client.get("/api/me")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
