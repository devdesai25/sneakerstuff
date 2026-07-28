import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth import get_current_user, req_admin
from backend.auth.jwt import encode
from backend.models.users import User

@pytest.mark.asyncio
async def test_get_current_user_success(db: AsyncSession, user: User):
    """Test get_current_user with a valid token."""
    token = encode({"sub": str(user.id)})
    current_user = await get_current_user(token=token, db=db)
    
    assert current_user.id == user.id
    assert current_user.username == user.username
    assert current_user.email == user.email

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db: AsyncSession):
    """Test get_current_user with an invalid token."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="invalid.token.here", db=db)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token Invalid"

@pytest.mark.asyncio
async def test_get_current_user_user_not_found(db: AsyncSession):
    """Test get_current_user when user is not in database."""
    # Create token for a non-existent user id (e.g. 9999)
    token = encode({"sub": "9999"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=db)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User Not Found"

def test_req_admin_success(admin_user: User):
    """Test req_admin dependency with an admin user."""
    returned_admin = req_admin(admin=admin_user)
    assert returned_admin.id == admin_user.id
    assert returned_admin.role == "admin"

def test_req_admin_forbidden(user: User):
    """Test req_admin dependency with a regular user."""
    with pytest.raises(HTTPException) as exc_info:
        req_admin(admin=user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Forbidden"
