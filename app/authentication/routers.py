from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from app.authentication.controllers import sign_up_user, authenticate_user, forgot_password as forgot_password_controller, reset_password, verify_email_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.authentication.models import User, UserCreate, UserLogin, UserResponse, PaginatedUserResponse
from fastapi.security import OAuth2PasswordBearer
from app.authentication.jwt import verify_access_token
from app.authentication.controllers import get_user_by_email, change_password, get_paginated_users
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Use the correct login endpoint

router = APIRouter()

@router.post("/sign-up")
async def sign_up(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    return await sign_up_user(user.email, user.password, db, background_tasks)


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(user.email, user.password, db)


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    return await verify_email_token(token, db)


# Use different function name to avoid recursion
@router.post("/forgot-password")
async def forgot_password_request(email: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    return await forgot_password_controller(email, db, background_tasks)


@router.get("/reset-password")
async def change_password(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
    return await reset_password(token, new_password, db)


@router.post("/change-password")
async def change_user_password(
    current_password: str,
    new_password: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Verify the access token
    user_email = await verify_access_token(token)

    # Change the password
    return await change_password(user_email, current_password, new_password, db)


@router.get("/who_am_i", response_model=UserResponse)
async def who_am_i(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    # Verify the access token and get the user's email
    user_email = verify_access_token(token)
    
    # Fetch the user from the database using their email
    user = await get_user_by_email(user_email, db)
    
    # If user is not found, return 401 Unauthorized
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")
    
    # Return the user's details
    return UserResponse(email=user.email, is_active=user.is_active, is_verified=user.is_verified)


# All users endpoint with cursor pagination
@router.get("/all_users", response_model=PaginatedUserResponse)
async def all_users(
    cursor: Optional[int] = None,  # The cursor (id of the last fetched user)
    limit: int = 10,  # Limit number of users per request (default to 10)
    db: AsyncSession = Depends(get_db)
):
    return await get_paginated_users(cursor, limit, db)
