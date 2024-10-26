from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from fastapi import HTTPException

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
def create_email_verification_token(email: str):
    data = {"sub": email, "purpose": "email_verification"}
    return create_access_token(data, expires_delta=timedelta(hours=24))

def verify_email_verification_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "email_verification":
            raise JWTError("Invalid token purpose")
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

def create_password_reset_token(email: str):
    data = {"sub": email, "purpose": "password_reset"}
    return create_access_token(data, expires_delta=timedelta(hours=1))

def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "password_reset":
            raise JWTError("Invalid token purpose")
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

