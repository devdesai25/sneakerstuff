import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_route_success(client: AsyncClient):
    """Test successful user registration via route."""
    response = await client.post(
        "/api/signup",
        json={
            "username": "routeruser",
            "email": "routeruser@example.com",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "routeruser"

@pytest.mark.asyncio
async def test_signup_route_duplicate_email(client: AsyncClient):
    """Test registration with existing email via route."""
    # Register first
    await client.post(
        "/api/signup",
        json={
            "username": "routeruser2",
            "email": "duplicate@example.com",
            "password": "securepassword123"
        }
    )
    
    # Try again
    response = await client.post(
        "/api/signup",
        json={
            "username": "routeruser3",
            "email": "duplicate@example.com",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_route_success(client: AsyncClient):
    """Test successful user login via route."""
    # First create a user
    await client.post(
        "/api/signup",
        json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "securepassword123"
        }
    )
    
    # Login (OAuth2PasswordRequestForm expects form data)
    response = await client.post(
        "/api/login",
        data={
            "username": "loginuser@example.com", # OAuth2 uses username for email
            "password": "securepassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_route_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials via route."""
    response = await client.post(
        "/api/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Password or Email"
