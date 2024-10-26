from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.jwt import create_access_token, verify_access_token, create_email_verification_token, \
    verify_email_verification_token, create_password_reset_token, verify_password_reset_token
from app.utils.email import send_email_verification, send_password_reset_email
from app.authentication.models import User
from app.authentication.schemas import UserListResponse, UserDetailResponse
from app.hero.models import Hero
from fastapi import HTTPException, BackgroundTasks, status
from passlib.context import CryptContext
from sqlalchemy import select, and_, desc, asc
from typing import Optional, List, Dict
import random
import string


# Function to generate a random username based on email
def generate_username(email: str) -> str:
    base_username = email.split('@')[0]
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    return f"{base_username}_{random_suffix}"

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
    username = generate_username(email)

    # Assign the default hero (Admiral Bubbles)
    default_hero = await db.get(Hero, 1)  # Assuming hero id 1 is Admiral Bubbles
    
    # Create new user
    # Create new user
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        username=username,
        hero=default_hero,  # Assign default hero
        gems=10,  # Default gems
        tokens=100,  # Default tokens
        skill_points=0,  # Default skill points
        games_played=0,  # Default games played
        ranked_games_played=0,  # Default ranked games played
        wins=0,  # Default wins
        losses=0,  # Default losses
        win_rate=0.0,  # Default win rate
        longest_win_streak=0,  # Default longest win streak
        longest_loss_streak=0,  # Default longest loss streak
    )

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


# Controller to handle user retrieval with pagination, sorting, and filters
async def list_users(
    db: AsyncSession,
    cursor: Optional[int] = None,
    limit: int = 50,  # Smaller page size, e.g., 50 results per page
    max_results: int = 1000,  # Max results a user can scroll down to
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    country_id: Optional[int] = None,
    skill_points_ffa: Optional[bool] = None,
    skill_points_1v1: Optional[bool] = None,
    sort_order: str = "desc",  # Can be 'asc' or 'desc'
    name: Optional[str] = None,  # New filter for name
    username: Optional[str] = None,  # New filter for username
    email: Optional[str] = None,  # New filter for email
) -> Dict:
    query = select(User).order_by(User.id).limit(limit)

    # Apply cursor (pagination)
    if cursor:
        query = query.where(User.id > cursor)

    # Apply filters (only the important ones)
    filters = []
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if is_verified is not None:
        filters.append(User.is_verified == is_verified)
    if country_id is not None:
        filters.append(User.country_id == country_id)
    if name:
        filters.append(User.name.ilike(f"%{name}%"))  # Case-insensitive name filter
    if username:
        filters.append(User.username.ilike(f"%{username}%"))  # Case-insensitive username filter
    if email:
        filters.append(User.email.ilike(f"%{email}%"))  # Case-insensitive email filter

    if filters:
        query = query.where(and_(*filters))

    # Apply sorting based on skill points (either FFA or 1v1)
    if skill_points_ffa:
        query = query.order_by(desc(User.skill_points_ffa) if sort_order == "desc" else asc(User.skill_points_ffa))
    if skill_points_1v1:
        query = query.order_by(desc(User.skill_points_1v1) if sort_order == "desc" else asc(User.skill_points_1v1))

    result = await db.execute(query)
    users = result.scalars().all()

    # Calculate the next cursor (if there are more results)
    next_cursor = users[-1].id if len(users) == limit and cursor + limit <= max_results else None

    return {
        "users": users,
        "next_cursor": next_cursor
    }
