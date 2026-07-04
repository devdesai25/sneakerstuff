# ==========================================
# SNEAKERSTUFF AUTH REFACTOR
# Modified by Sneakerstuff Developer
# Purpose:
# Authentication now uses email instead of username.
# ==========================================

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import hash_password, encode, verify
from backend.models.users import User
from backend.schemas.users import UserSignup

async def signup_service(
    user: UserSignup, 
    db: AsyncSession
) -> dict:
    """Register a new user, validating unique username and email addresses."""
    
    # 1. Uniqueness check on username
    existing_username = (
        await db.execute(
            select(User).where(User.username == user.username)
        )
    ).scalar_one_or_none()
    
    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already taken"
        )

    # 2. Uniqueness check on email address
    existing_email = (
        await db.execute(
            select(User).where(User.email == user.email)
        )
    ).scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # 3. Create the user database record with email saved to db
    new_user = User(
        username = user.username, 
        email = user.email,
        hashed_password = hash_password(user.password)
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
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

    # 4. Generate token payload containing user id, username, and email
    access_token = encode(
         {
         "sub": str(new_user.id),
         "username": new_user.username,
         "email": new_user.email
        }
    )

    return (
        {
            "access_token": access_token,
            "token_type": "bearer",
            "user":{
                "id" : new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role 
            }
        }
    )


async def login_service(
    form_data: OAuth2PasswordRequestForm, 
    db: AsyncSession
) -> dict:
    """Authenticate users by looking up the email column (mapped from OAuth2 username)."""
    
    # Perform database lookup against the User.email column
    # OAuth2PasswordRequestForm passes the email address in the 'username' field.
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
            
    if not verify(form_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password or Email"
        )
     
    # Embed sub (id), username, and email in JWT claims
    access_token = encode({
        "sub": str(existing_user.id),
        "username": existing_user.username,
        "email": existing_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }