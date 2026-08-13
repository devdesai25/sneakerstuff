from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import encode, hash_password_async, verify_async
from backend.models.users import User
from backend.schemas.users import UserSignup


async def signup_service(
    user: UserSignup, 
    db: AsyncSession
) -> dict:
    """Register a new user, validating unique username and email addresses in a single query."""
    
    # 1. Single combined uniqueness check for username or email
    stmt = select(User).where(or_(User.username == user.username, User.email == user.email))
    existing_user = (await db.execute(stmt)).scalars().first()
    
    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=409,
                detail="Username already taken"
            )
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

    # 2. Create the user database record
    hashed = await hash_password_async(user.password)
    new_user = User(
        username=user.username, 
        email=user.email,
        hashed_password=hashed
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    except Exception:
        await db.rollback()
        raise

    # 3. Generate token payload
    access_token = encode({
        "sub": str(new_user.id),
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role 
        }
    }


async def login_service(
    form_data: OAuth2PasswordRequestForm, 
    db: AsyncSession
) -> dict:
    """Authenticate users by looking up the email column (mapped from OAuth2 username)."""
    if not form_data or not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password or Email"
        )

    existing_user = (
        await db.execute(
            select(User).where(User.email == form_data.username)
        )
    ).scalar_one_or_none()
        
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password or Email"
        )
            
    is_valid = await verify_async(form_data.password, existing_user.hashed_password)
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password or Email"
        )
     
    access_token = encode({
        "sub": str(existing_user.id),
        "username": existing_user.username,
        "email": existing_user.email,
        "role": existing_user.role or "user"
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }