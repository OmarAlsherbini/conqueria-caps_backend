from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.jwt import create_access_token, verify_access_token, create_email_verification_token, \
    verify_email_verification_token, create_password_reset_token, verify_password_reset_token
from app.utils.email import send_email_verification, send_password_reset_email
from app.authentication.models import User, PaginatedUserResponse, UserResponse
from fastapi import HTTPException, BackgroundTasks, status
from passlib.context import CryptContext
from sqlalchemy import select
from typing import Optional, List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sign up user and send verification email
async def sign_up_user(email: str, password: str, db: AsyncSession, background_tasks: BackgroundTasks):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Create new user
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
     
    # Generate verification token
    verification_token = create_email_verification_token(new_user.email)
    send_email_verification(background_tasks, new_user.email, verification_token)
    
    return new_user


async def authenticate_user(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Reset password using token
async def reset_password(token: str, new_password: str, db: AsyncSession):
    email = verify_password_reset_token(token)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = pwd_context.hash(new_password)
    await db.commit()
    return {"message": "Password updated successfully"}


async def change_password(user_id: int, current_password: str, new_password: str, db: AsyncSession):
    # Retrieve user from database
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if current password is correct
    if not pwd_context.verify(current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

    # Hash and update new password
    hashed_new_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_new_password

    # Commit changes to DB
    db.add(user)
    await db.commit()

    return {"message": "Password changed successfully"}


# Verify email token and activate user
async def verify_email_token(token: str, db: AsyncSession):
    email = verify_email_verification_token(token)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}


# Forgot password and send reset token
async def forgot_password(email: str, db: AsyncSession, background_tasks: BackgroundTasks):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_token = create_password_reset_token(user.email)
    send_password_reset_email(background_tasks, user.email, reset_token)
    return {"message": "Password reset email sent"}


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if a plaintext password matches a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Utility to get user by email
async def get_user_by_email(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user


# Pagination function with cursor logic
async def get_paginated_users(cursor: Optional[int], limit: int, db: AsyncSession) -> PaginatedUserResponse:
    query = select(User).order_by(User.id).limit(limit)

    # If cursor (i.e., last fetched user id) is provided, fetch users after that ID
    if cursor:
        query = query.where(User.id > cursor)

    result = await db.execute(query)
    users = result.scalars().all()

    # Determine the next cursor (id of the last user returned)
    next_cursor = users[-1].id if users else None

    # Format the response using Pydantic schema
    users_response = [UserResponse(email=user.email, is_active=user.is_active, is_verified=user.is_verified) for user in users]
    
    return PaginatedUserResponse(users=users_response, next_cursor=next_cursor)