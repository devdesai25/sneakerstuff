from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from backend.database import get_db
from backend.models.users import User
from backend.auth.jwt import hash_password, encode, verify, encode

def signup_service(user, db):
           
    db_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
        )
    
    if db_user:

        raise HTTPException(
            status_code=409,
            detail="Username already there"
        )
    
    hashed_pass = hash_password(user.password)

    db_user = User(
        username = user.username, 
        hashed_password = hashed_pass
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    
    token = {"sub":db_user.id,"username":db_user.username}

    access_token = encode(token)

    return (
        {
            "access_token": access_token,
            "token_type": "bearer",
            "user":{
                "id" : db_user.id,
                "username": db_user.username,
                "role": db_user.role 
            }
        }
    )


def login_service(user, db):
    
    db_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
        )
    
    if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid Password or Username"
                )
            
    if not verify(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid Password Or Username"
                )
        
    user_id = db_user.id 
        
    access_token = encode({
                "sub":str(user_id),
                "username":db_user.username
            })

    return {
            "access_token":access_token,
            "token_type":"bearer"
        }