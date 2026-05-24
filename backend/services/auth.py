from auth.jwt import decode, oauth2scheme
from fastapi import Depends, HTTPException
from database import get_db
from models.users import User
from schemas.users import UserLogin

def get_current_user(
        token = Depends(oauth2scheme), 
        db = Depends(get_db)
):
    
    payload =  decode(token)
    
    if not payload:
        raise HTTPException(401,detail="Token Invalid")
    
    user_id = payload.get('sub')
    
    user =  (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    
    if not user:
        raise HTTPException(
            401,
            detail="User Not Found"
        )
    print(user.id)
    return user

def req_admin(
        admin = Depends(get_current_user)
):

    if not admin.role == 'admin':
        
        raise HTTPException(
            status_code=403,
            detail= "Forbidden"
        )
    
    return admin