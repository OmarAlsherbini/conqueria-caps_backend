from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from app.authentication.controllers import sign_up_user, authenticate_user, forgot_password as forgot_password_controller, reset_password, verify_email_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.authentication.jwt import verify_access_token, oauth2_scheme
from app.authentication.controllers import get_user_by_email, change_password, list_users
from app.authentication.schemas import UserListResponse, UserCreate, UserLogin, UserResponse
from typing import Optional, List

router = APIRouter(tags=["Authentication & Users"])

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
    
    # If user is not found, return 404 Unauthorized
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the user's details
    return UserResponse(email=user.email, is_active=user.is_active, is_verified=user.is_verified)


# GET all users with pagination, sorting, and filters
@router.get("/users", response_model=List[UserListResponse])
async def get_users(
    cursor: Optional[int] = None,
    limit: int = Query(50, description="Results per page (default 50)"),
    max_results: int = Query(1000, description="Maximum of 1000 results in total"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by email verification status"),
    country_id: Optional[int] = Query(None, description="Filter by country ID"),
    skill_points_ffa: Optional[bool] = Query(None, description="Sort by FFA skill points"),
    skill_points_1v1: Optional[bool] = Query(None, description="Sort by 1v1 skill points"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    name: Optional[str] = Query(None, description="Filter by name"),
    username: Optional[str] = Query(None, description="Filter by username"),
    email: Optional[str] = Query(None, description="Filter by email"),
    db: AsyncSession = Depends(get_db)
):
    response = await list_users(
        db, cursor, limit, max_results, is_active, is_verified, country_id, 
        skill_points_ffa, skill_points_1v1, sort_order, name, username, email
    )
    return {
        "users": response["users"],
        "next_cursor": response["next_cursor"]
    }


