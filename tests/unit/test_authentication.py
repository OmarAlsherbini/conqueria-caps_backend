# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy.ext.asyncio import AsyncSession

# # Make sure to add pytest-asyncio marker for async tests
# pytestmark = pytest.mark.asyncio

# # Testing the signup functionality
# async def test_sign_up_user(client: TestClient, test_db: AsyncSession):
#     signup_data = {"email": "newuser@example.com", "password": "Password123!"}
#     response = client.post("/sign-up", json=signup_data)

#     assert response.status_code == 200
#     assert response.json()["email"] == "newuser@example.com"
#     assert response.json()["is_active"] is True
#     assert response.json()["is_verified"] is False  # Assuming email verification is pending


# # Testing the login functionality
# async def test_login_user(client: TestClient, test_db: AsyncSession, test_user):
#     login_data = {"email": test_user.email, "password": "Password123!"}  # Use correct password
#     response = client.post("/login", json=login_data)

#     assert response.status_code == 200
#     assert "access_token" in response.json()


# # Testing the change password functionality (with token in header)
# async def test_change_password(client: TestClient, test_db: AsyncSession, auth_token):
#     headers = {"Authorization": f"Bearer {auth_token}"}
#     change_password_data = {"old_password": "Password123!", "new_password": "NewPassword123!"}
#     response = client.post("/change-password", json=change_password_data, headers=headers)

#     assert response.status_code == 200
#     assert response.json()["message"] == "Password changed successfully"


# # Testing forgot password
# async def test_forgot_password(client: TestClient, test_db: AsyncSession, test_user):
#     forgot_password_data = {"email": test_user.email}
#     response = client.post("/forgot-password", json=forgot_password_data)

#     assert response.status_code == 200
#     assert response.json()["message"] == "Password reset link sent"
