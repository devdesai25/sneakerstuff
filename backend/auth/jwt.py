from passlib.context import CryptContext
from jose import jwt,JWTError
import json
from datetime import timedelta, datetime
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt_sha256","bcrypt"], deprecated="auto")

def hash_password(password:str):
    hashed_password = pwd_context.hash(password)
    return hashed_password

def verify(plain_password:str,hash_password:str):
    plain_password = pwd_context.verify(plain_password, hash_password)
    return plain_password

def encode(data:dict):
    assert isinstance(data,dict)    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded = jwt.encode(to_encode , settings.SECRET_KEY, algorithm= settings.SECRET_ALGORITHM)
    return encoded

def decode(data):
    try:
        payload = jwt.decode(data, settings.SECRET_KEY,algorithms=[settings.SECRET_ALGORITHM])
        return payload
    except JWTError as e:
        print("JWT ERROR",e)
        return None
    
oauth2scheme = OAuth2PasswordBearer(tokenUrl = "/login")