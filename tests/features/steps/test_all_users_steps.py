import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.authentication.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from anyio import to_thread

client = TestClient(app)

# Properly handle the database session for tests
@pytest.fixture(scope="function")
async def db_session():
    async with SessionLocal() as session:
        yield session

# Seed the database with test users
@pytest.fixture(scope="function")
async def seed_registered_users(db_session: AsyncSession):
    users = [
        User(email="user1@example.com", hashed_password="password1", is_active=True, is_verified=True),
        User(email="user2@example.com", hashed_password="password2", is_active=True, is_verified=True),
        User(email="user3@example.com", hashed_password="password3", is_active=True, is_verified=True),
    ]
    db_session.add_all(users)
    await db_session.commit()

@pytest.mark.asyncio
@pytest.mark.usefixtures("seed_registered_users")
async def test_fetch_the_first_set_of_users():
    """Test fetching the first set of users"""
    # Run the request in a thread because FastAPI TestClient is synchronous
    response = await to_thread.run_sync(lambda: client.get("/all_users?limit=2"))
    
    assert response.status_code == 200
    data = response.json()

    # Ensure that the response contains users and is paginated
    assert len(data["users"]) == 2
    assert "next_cursor" in data
    assert data["next_cursor"] is not None

@pytest.mark.asyncio
@pytest.mark.usefixtures("seed_registered_users")
async def test_fetch_the_next_set_of_users():
    """Test fetching the next set of users using the cursor"""
    # Run the first request in a thread
    first_response = await to_thread.run_sync(lambda: client.get("/all_users?limit=2"))
    first_data = first_response.json()
    cursor = first_data["next_cursor"]

    # Run the next request in a thread
    second_response = await to_thread.run_sync(lambda: client.get(f"/all_users?cursor={cursor}&limit=2"))
    second_data = second_response.json()

    # Ensure that the next set of users is fetched and pagination works
    assert second_response.status_code == 200
    assert len(second_data["users"]) <= 2
    assert "next_cursor" in second_data
    assert second_data["next_cursor"] is not None
