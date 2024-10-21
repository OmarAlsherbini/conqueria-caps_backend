from pytest_bdd import scenarios, given, when, then
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import insert
from app.db.session import get_db
from app.authentication.models import User

client = TestClient(app)
scenarios("../all_users.feature")

# Fixture to seed users in the system
@given("there are registered users in the system")
async def seed_registered_users():
    async with get_db() as db:
        users = [
            {"email": "bdd_user1@example.com", "hashed_password": "password1", "is_active": True, "is_verified": True},
            {"email": "bdd_user2@example.com", "hashed_password": "password2", "is_active": True, "is_verified": True},
        ]
        for user in users:
            query = insert(User).values(user)
            await db.execute(query)
        await db.commit()

@when("I request the first page of users")
def request_first_page():
    response = client.get("/all_users?limit=5")
    return response

@then("I should receive a list of users")
def check_user_list(request_first_page):
    assert request_first_page.status_code == 200
    json_response = request_first_page.json()
    assert "users" in json_response
    assert len(json_response["users"]) > 0

@then("the list should be paginated")
def check_pagination(request_first_page):
    json_response = request_first_page.json()
    assert "next_cursor" in json_response

@then("I should see the cursor for the next set of users")
def check_next_cursor(request_first_page):
    json_response = request_first_page.json()
    assert json_response["next_cursor"] is not None

@given("I have the cursor from the first page")
def get_cursor_from_first_page(request_first_page):
    json_response = request_first_page.json()
    return json_response["next_cursor"]

@when("I request the next set of users using the cursor")
def request_next_page(get_cursor_from_first_page):
    cursor = get_cursor_from_first_page
    response = client.get(f"/all_users?cursor={cursor}&limit=5")
    return response

@then("I should receive the next set of users")
def check_next_user_list(request_next_page):
    assert request_next_page.status_code == 200
    json_response = request_next_page.json()
    assert "users" in json_response
    assert len(json_response["users"]) > 0
