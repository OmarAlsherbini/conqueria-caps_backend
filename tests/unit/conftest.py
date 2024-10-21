import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, SessionLocal
from app.authentication.models import User
from sqlalchemy import insert
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_override():
    async with SessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def db_session_override():
    async with get_db_override() as session:
        yield session

# Seed test users into the database
@pytest.fixture(scope="function", autouse=True)
async def seed_test_data(db_session_override: AsyncSession):
    users = [
        {"email": "user1@example.com", "hashed_password": "password1", "is_active": True, "is_verified": True},
        {"email": "user2@example.com", "hashed_password": "password2", "is_active": True, "is_verified": True},
    ]

    for user in users:
        query = insert(User).values(user)
        await db_session_override.execute(query)

    await db_session_override.commit()

    yield  # Test runs here

    # Clean up after test
    await db_session_override.execute("TRUNCATE TABLE users RESTART IDENTITY")
    await db_session_override.commit()














# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import sessionmaker
# from app.db.session import engine
# from app.db.base_class import Base
# from app.authentication.models import User
# from app.authentication.jwt import create_access_token
# from app.authentication.controllers import hash_password

# # Database Fixture
# @pytest.fixture(scope="function")
# async def test_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     SessionTesting = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
#     async with SessionTesting() as session:
#         yield session
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# # User Fixture
# @pytest.fixture(scope="function")
# async def test_user(test_db: AsyncSession):
#     user_data = {
#         "email": "testuser@example.com",
#         "hashed_password": hash_password("Password123!"),
#         "is_active": True,
#         "is_verified": True
#     }
#     new_user = User(**user_data)
#     test_db.add(new_user)
#     await test_db.commit()
#     await test_db.refresh(new_user)
#     return new_user


# # JWT Token Fixture
# @pytest.fixture(scope="function")
# async def auth_token(test_user):
#     user = test_user
#     return create_access_token({"sub": user.email})


# # Client Fixture: Provide a FastAPI TestClient to simulate HTTP requests
# @pytest.fixture(scope="module")
# def client():
#     from app.main import app  # Import inside the fixture to avoid circular imports
#     from fastapi.testclient import TestClient
#     with TestClient(app) as test_client:
#         yield test_client
