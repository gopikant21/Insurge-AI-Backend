import pytest
from fastapi.testclient import TestClient
from app.schemas.user import UserCreate


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Insurge AI Backend API"
    assert data["version"] == "1.0.0"


def test_health_endpoint(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # Might fail if Redis isn't running
    data = response.json()
    assert "status" in data
    assert "environment" in data
    assert "version" in data


def test_register_user(client: TestClient, cleanup_db):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email(client: TestClient, cleanup_db):
    """Test registration with duplicate email."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }

    # Register first user
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    # Try to register with same email
    user_data["username"] = "testuser2"
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_user(client: TestClient, cleanup_db):
    """Test user login."""
    # First register a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # Now login
    login_data = {"email": "test@example.com", "password": "testpassword123"}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, cleanup_db):
    """Test login with invalid credentials."""
    login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user(client: TestClient, cleanup_db):
    """Test getting current user profile."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }

    client.post("/api/v1/auth/register", json=user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]


def test_unauthorized_access(client: TestClient):
    """Test access without authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403
