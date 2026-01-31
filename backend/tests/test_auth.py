import requests

BASE_URL = "http://localhost:8000"

# Test user data
# Use a password >72 characters to test backend truncation logic
test_user = {
    "email": "testuser@example.com",
    "password": "A" * 80,  # 80 characters, triggers backend truncation to 71 bytes
    "full_name": "Test User",
}


def test_register(register_user):
    # Registration is handled in the fixture; this test just ensures the fixture runs
    assert register_user["email"] == test_user["email"]


def test_login(access_token):
    # Login is handled in the fixture; this test just ensures the fixture runs
    assert access_token is not None


def test_me(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert resp.status_code == 200


def test_me_no_token():
    resp = requests.get(f"{BASE_URL}/users/me")
    assert resp.status_code == 401


def test_me_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken123"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert resp.status_code == 401


# --- Additional edge case tests ---
def test_register_invalid_email():
    bad_user = {
        "email": "not-an-email",
        "password": "ValidPass123!",  # pragma: allowlist secret
        "full_name": "Bad Email",
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=bad_user)
    assert resp.status_code == 422 or resp.status_code == 400


def test_register_short_password():
    bad_user = {
        "email": "shortpass@example.com",
        "password": "123",
        "full_name": "Short Pass",
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=bad_user)
    assert resp.status_code == 422 or resp.status_code == 400


def test_register_duplicate_user(register_user):
    resp = requests.post(f"{BASE_URL}/auth/register", json=register_user)
    assert resp.status_code == 400


def test_login_wrong_password():
    data = {"username": test_user["email"], "password": "WrongPassword123!"}
    resp = requests.post(f"{BASE_URL}/auth/login", data=data)
    assert resp.status_code == 400 or resp.status_code == 401


def test_login_nonexistent_user():
    data = {
        "username": "nouser@example.com",
        "password": "AnyPassword123!",  # pragma: allowlist secret
    }
    resp = requests.post(f"{BASE_URL}/auth/login", data=data)
    assert resp.status_code == 400 or resp.status_code == 401
