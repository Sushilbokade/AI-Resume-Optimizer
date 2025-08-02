import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "user_id" in data

def test_login_user():
    """Test user login"""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "login@example.com", 
            "password": "TestPassword123"
        }
    )

    # Then try to login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "invalid@example.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401

def test_get_current_user():
    """Test getting current user info"""
    # Register and login first
    client.post(
        "/api/auth/register",
        json={
            "name": "Current User",
            "email": "current@example.com",
            "password": "TestPassword123"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "current@example.com",
            "password": "TestPassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Get user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["name"] == "Current User"
