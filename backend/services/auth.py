from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.users import User
from backend.auth.jwt import decode, oauth2scheme

async def get_current_user(
        token: str = Depends(oauth2scheme), 
        db: AsyncSession = Depends(get_db)
) -> User:
    
    payload = decode(token)
    
    if not payload:
        raise HTTPException(401,detail="Token Invalid")
    
    "JWT stroes as string so convert it to integer"
    user_id = int(payload.get('sub'))
    
    user = (
        await db.execute(
            select(User).where(User.id == user_id)
        )
    ).scalar_one_or_none()  

    if not user:
        raise HTTPException(
            401,
            detail="User Not Found"
        )
    
    return user

def req_admin(
    admin: User = Depends(get_current_user)
) -> User:

    if admin.role != 'admin':
        
        raise HTTPException(
            status_code=403,
            detail= "Forbidden"
        )
    
    return admin