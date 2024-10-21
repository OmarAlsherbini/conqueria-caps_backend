from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test fetching users with pagination
def test_get_users_with_pagination():
    response = client.get("/all_users?limit=5")
    assert response.status_code == 200
    json_response = response.json()

    # Check that the response contains users and a next cursor
    assert "users" in json_response
    assert len(json_response["users"]) > 0
    assert "next_cursor" in json_response

# Test fetching next page using cursor
def test_get_next_page_users():
    response = client.get("/all_users?limit=5")
    json_response = response.json()
    cursor = json_response["next_cursor"]

    next_page_response = client.get(f"/all_users?cursor={cursor}&limit=5")
    assert next_page_response.status_code == 200
    json_response = next_page_response.json()

    # Check that the response contains users and a next cursor
    assert "users" in json_response
    assert len(json_response["users"]) > 0
    assert "next_cursor" in json_response
