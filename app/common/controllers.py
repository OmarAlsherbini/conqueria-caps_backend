from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from app.authentication.models import User
from app.authentication.jwt import verify_access_token

# Common function to check if the user is an admin
async def verify_admin_access(token: str, db: AsyncSession) -> User:
    user_email = await verify_access_token(token)
    user = await db.execute(select(User).where(User.email == user_email))
    user = user.scalars().first()

    # Check if the user exists and is an admin
    if not user or not user.is_admin_user():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return user
