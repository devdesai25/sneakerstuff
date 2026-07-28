import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock

from backend.services.users import signup_service, login_service
from backend.schemas.users import UserSignup
from backend.models.users import User
from backend.auth.jwt import verify

@pytest.mark.asyncio
async def test_signup_service_success(db: AsyncSession):
    """Test successful user registration."""
    user_data = UserSignup(
        username="newuser",
        email="newuser@example.com",
        password="securepassword123"
    )
    
    response = await signup_service(user=user_data, db=db)
    
    assert "access_token" in response
    assert response["token_type"] == "bearer"
    assert response["user"]["username"] == "newuser"
    assert response["user"]["email"] == "newuser@example.com"
    assert response["user"]["role"] == "user"
    
    # Verify user is in database
    db_user = (
        await db.execute(select(User).where(User.username == "newuser"))
    ).scalar_one_or_none()
    
    assert db_user is not None
    assert db_user.email == "newuser@example.com"
    assert verify("securepassword123", db_user.hashed_password)

@pytest.mark.asyncio
async def test_signup_service_username_taken(db: AsyncSession, user: User):
    """Test registration with an already taken username."""
    user_data = UserSignup(
        username=user.username,
        email="differentemail@example.com",
        password="securepassword123"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await signup_service(user=user_data, db=db)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Username already taken"

@pytest.mark.asyncio
async def test_signup_service_email_taken(db: AsyncSession, user: User):
    """Test registration with an already taken email."""
    user_data = UserSignup(
        username="differentuser",
        email=user.email,
        password="securepassword123"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await signup_service(user=user_data, db=db)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already registered"

@pytest.mark.asyncio
async def test_signup_service_integrity_error(db: AsyncSession):
    """Test registration when a database integrity error occurs."""
    user_data = UserSignup(
        username="integrity_test",
        email="integrity@example.com",
        password="securepassword123"
    )
    
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
        from sqlalchemy.exc import IntegrityError
        # Provide the required positional arguments for IntegrityError
        mock_commit.side_effect = IntegrityError(None, None, Exception())
        
        with pytest.raises(HTTPException) as exc_info:
            await signup_service(user=user_data, db=db)
            
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Database Integrity Error"

@pytest.mark.asyncio
async def test_login_service_success(db: AsyncSession, user: User):
    """Test successful user login."""
    # Since factory sets password to "password123" via hash_password
    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username=user.email,  # OAuth2 uses username field for email
        password="password123",
        scope="",
        client_id=None,
        client_secret=None
    )
    
    response = await login_service(form_data=form_data, db=db)
    
    assert "access_token" in response
    assert response["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_service_invalid_email(db: AsyncSession):
    """Test user login with invalid email."""
    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username="nonexistent@example.com",
        password="password123",
        scope="",
        client_id=None,
        client_secret=None
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await login_service(form_data=form_data, db=db)
        
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Password or Email"

@pytest.mark.asyncio
async def test_login_service_invalid_password(db: AsyncSession, user: User):
    """Test user login with invalid password."""
    form_data = OAuth2PasswordRequestForm(
        grant_type="password",
        username=user.email,
        password="wrongpassword",
        scope="",
        client_id=None,
        client_secret=None
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await login_service(form_data=form_data, db=db)
        
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Password or Email"
