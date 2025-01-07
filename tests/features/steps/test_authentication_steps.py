# import pytest
# from pytest_bdd import scenarios, given, when, then
# from fastapi.testclient import TestClient
# from app.main import app
# from app.db.session import get_db
# from app.authentication.models import User
# from app.authentication.controllers import hash_password

# client = TestClient(app)

# # Load the Gherkin feature file
# scenarios('../authentication.feature')


# # --- Step Definitions ---

# # Scenario: User signs up
# @given("the user provides a valid email and password")
# def valid_user_data():
#     return {"email": "testuser@example.com", "password": "Password123!"}


# @when("the user submits the sign-up form")
# def submit_sign_up_form(valid_user_data):
#     response = client.post("/sign-up", json=valid_user_data)
#     return response


# @then("the user receives a verification email")
# def verify_email(submit_sign_up_form):
#     assert submit_sign_up_form.status_code == 200
#     # You can mock email sending for actual testing if necessary.


# # Scenario: User verifies email
# @given("the user has received a verification email")
# def user_has_verification_email(valid_user_data):
#     # Simulate the user having a verification email, typically this would be mocked.
#     return valid_user_data


# @when("the user clicks the verification link")
# def user_clicks_verification_link(valid_user_data):
#     # Simulate clicking the verification link by calling the API
#     verification_token = "dummy_token"  # Normally, you'd extract this from the email
#     response = client.get(f"/verify-email?token={verification_token}")
#     return response


# @then("the user’s email is marked as verified in the system")
# def email_verified_in_system(valid_user_data):
#     db = next(get_db())
#     user = db.query(User).filter_by(email=valid_user_data['email']).first()
#     assert user.is_verified is True


# # Scenario: User logs in
# @given("the user has verified their email")
# def verified_user_data(valid_user_data):
#     db = next(get_db())
#     user = db.query(User).filter_by(email=valid_user_data['email']).first()
#     if not user:
#         user = User(email=valid_user_data['email'], hashed_password=hash_password(valid_user_data['password']), is_verified=True)
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#     return valid_user_data


# @when("the user submits the login form")
# def submit_login_form(verified_user_data):
#     response = client.post("/login", json=verified_user_data)
#     return response


# @then("the user is authenticated and receives a JWT token")
# def authenticated_with_jwt(submit_login_form):
#     assert submit_login_form.status_code == 200
#     assert "access_token" in submit_login_form.json()


# # Scenario: User forgets password
# @given("the user has forgotten their password")
# def forgotten_password_user_data(valid_user_data):
#     return valid_user_data


# @when("the user requests a password reset")
# def request_password_reset(forgotten_password_user_data):
#     response = client.post("/forgot-password", json={"email": forgotten_password_user_data['email']})
#     return response


# @then("the user receives a reset link in their email")
# def verify_password_reset_email(request_password_reset):
#     assert request_password_reset.status_code == 200
#     # You can mock email sending for actual testing if necessary.


# # Scenario: User resets password
# @given("the user has received a reset password link")
# def received_reset_password_link(forgotten_password_user_data):
#     # Mock the password reset link
#     return forgotten_password_user_data


# @when("the user submits a new password with the link")
# def submit_new_password_with_link(received_reset_password_link):
#     reset_token = "dummy_token"  # Mock token
#     response = client.post(f"/reset-password?token={reset_token}", json={"new_password": "NewPassword456!"})
#     return response


# @then("the user’s password is updated")
# def password_is_updated(submit_new_password_with_link):
#     assert submit_new_password_with_link.status_code == 200
#     assert submit_new_password_with_link.json()["message"] == "Password updated successfully"


# # Scenario: User changes password
# @given("the user is logged in and authenticated")
# def logged_in_user_data(auth_token):
#     return {"Authorization": f"Bearer {auth_token}"}


# @when("the user submits the change password request")
# def submit_change_password_request(logged_in_user_data):
#     response = client.post("/change-password", json={"old_password": "Password123!", "new_password": "NewPassword456!"}, headers=logged_in_user_data)
#     return response


# @then("the user’s password is updated")
# def password_change_is_successful(submit_change_password_request):
#     assert submit_change_password_request.status_code == 200
#     assert submit_change_password_request.json()["message"] == "Password changed successfully"


# # Scenario: User tries to change password without being authenticated
# @given("the user is not authenticated")
# def unauthenticated_user_data():
#     return {}


# @when("the user tries to submit a change password request")
# def submit_unauthenticated_change_password_request(unauthenticated_user_data):
#     response = client.post("/change-password", json={"old_password": "Password123!", "new_password": "NewPassword456!"})
#     return response


# @then("the system denies the request with a 401 Unauthorized error")
# def unauthorized_error(submit_unauthenticated_change_password_request):
#     assert submit_unauthenticated_change_password_request.status_code == 401


# # Scenario: User provides incorrect current password
# @given("the user is authenticated")
# def authenticated_user_data(auth_token):
#     return {"Authorization": f"Bearer {auth_token}"}


# @when("the user provides an incorrect current password")
# def submit_incorrect_current_password(authenticated_user_data):
#     response = client.post("/change-password", json={"old_password": "WrongPassword!", "new_password": "NewPassword456!"}, headers=authenticated_user_data)
#     return response


# @then("the system denies the request with a 400 Bad Request error")
# def incorrect_password_error(submit_incorrect_current_password):
#     assert submit_incorrect_current_password.status_code == 400
#     assert "incorrect" in submit_incorrect_current_password.json()["detail"].lower()
