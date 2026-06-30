from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import hash_password, encode, verify
from backend.models.users import User
from backend.schemas.users import UserSignup

async def signup_service(user: User, db: AsyncSession):  
    existing_user = (
        await db.execute(
            select(User).where(User.username == user.username)
        )
    ).scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already there"
        )

    new_user = User(
        username = user.username, 
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

    access_token = encode(
         {
         "sub": str(new_user.id),
         "username": new_user.username
        }
    )

    return (
        {
            "access_token": access_token,
            "token_type": "bearer",
            "user":{
                "id" : new_user.id,
                "username": new_user.username,
                "role": new_user.role 
            }
        }
    )


async def login_service(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    
    existing_user = (
        await db.execute(
            select(User).where(User.username == form_data.username)
        )
    ).scalar_one_or_none()
        
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password or Username"
        )
            
    if not verify(form_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password Or Username"
        )
     
    access_token = encode({
        "sub":str(existing_user.id),
        "username":existing_user.username
        }
    )

    return {
        "access_token":access_token,
        "token_type":"bearer"
    }