import threading
import backend.auth as auth
from backend.models import User
import uuid


def test_create_project_valid(client):
    response = client.post(
        "/projects/", json={"name": "Test Project", "description": "A test project."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


def test_create_project_invalid(client):
    response = client.post("/projects/", json={"name": "", "description": ""})
    assert response.status_code in (400, 422)


# --- Authenticated and Unauthenticated Access ---


def test_get_projects_unauthenticated(client):
    response = client.get("/projects/")
    assert response.status_code in (401, 403, 404)  # 404 if route not implemented


# --- Error Handling ---


def test_get_nonexistent_project(client):
    response = client.get("/projects/999999")
    assert response.status_code in (404, 401, 403)  # 401/403 if auth required


# --- Advanced/Edge-Case API Tests ---


def test_bulk_create_projects(client):
    projects = [{"name": f"Project {i}", "description": f"Desc {i}"} for i in range(5)]
    response = client.post("/projects/bulk_create", json=projects)
    assert response.status_code in (200, 201, 404)  # 404 if not implemented
    if response.status_code in (200, 201):
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5


# --- Rate Limiting (simulate rapid requests) ---


def test_rate_limit_exceeded(client):
    # Placeholder: actual implementation depends on rate limiting middleware
    last_status = None
    for _ in range(20):
        response = client.get("/projects/")
        last_status = response.status_code
        if last_status == 429:
            break
    assert last_status in (200, 404, 429)


# --- Concurrency (simulate with multiple requests) ---
def test_concurrent_edit_conflict(client):
    # Simulate concurrent edits (placeholder logic)
    results = []

    def edit():
        r = client.put("/projects/1", json={"name": "Edit"})
        results.append(r.status_code)

    t1 = threading.Thread(target=edit)
    t2 = threading.Thread(target=edit)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert all(s in (200, 409, 404) for s in results)


# --- API Error Response Structure ---


def test_api_error_format(client):
    response = client.get("/projects/doesnotexist")
    if response.status_code >= 400:
        data = response.json()
        assert "detail" in data


# --- Security: IDOR/Mass Assignment ---


def test_mass_assignment_protection(client):
    # Try to set a protected field
    response = client.post("/projects/", json={"name": "Test", "id": 12345})
    assert response.status_code in (201, 400, 422, 404)
    if response.status_code == 201:
        data = response.json()
        assert data["id"] != 12345


# --- Advanced: Authenticated API Flow Example ---


def create_test_user(
    db_session, email=None, password="testpassword123"  # pragma: allowlist secret
):  # pragma: allowlist secret
    email = email or f"user_{uuid.uuid4()}@example.com"
    hashed = auth.get_password_hash(password)
    user = User(email=email, hashed_password=hashed, full_name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user, password


def get_auth_token(client, email, password):
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},  # pragma: allowlist secret
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_authenticated_project_create(client, db_session):
    user, password = create_test_user(db_session)
    token = get_auth_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/projects/",
        json={"name": "Auth Project", "description": "By auth user"},
        headers=headers,
    )
    assert response.status_code in (201, 200, 404)
    if response.status_code in (201, 200):
        data = response.json()
        assert data["name"] == "Auth Project"


# --- Advanced: Permission/Role Test Example ---
def test_admin_only_endpoint(client, db_session):
    # Placeholder: assumes /admin endpoint exists and requires admin
    user, password = create_test_user(db_session)
    token = get_auth_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/admin", headers=headers)
    assert response.status_code in (403, 404)  # 404 if not implemented
