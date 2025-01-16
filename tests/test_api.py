import pytest
from fastapi.testclient import TestClient
from src.main import app
import uuid
from unittest.mock import Mock

client = TestClient(app)


@pytest.fixture
def mock_supabase(mocker):
    mock_client = Mock()
    # Mock user table operations
    mock_table = Mock()
    mock_client.table.return_value = mock_table

    # Mock select operation
    mock_select = Mock()
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_select
    mock_select.execute.return_value = Mock(data=[])

    # Mock insert operation
    mock_table.insert.return_value = Mock()
    mock_table.insert.return_value.execute.return_value = Mock(data=[{"id": 1}])

    # Patch the supabase client
    mocker.patch("src.main.supabase", mock_client)
    return mock_client


@pytest.fixture
def user_credentials():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "name": "Test User",
        "password": "securepassword",
    }


def test_signup(user_credentials):
    response = client.post(
        "/v1/auth/signup",
        json=user_credentials,
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Successfull"}


def test_login(user_credentials):
    # Ensure the user is signed up before logging in
    client.post(
        "/v1/auth/signup",
        json=user_credentials,
    )
    response = client.post(
        "/v1/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert response.status_code == 200
    assert "token" in response.json()
    return response.json()["token"]


def test_check_auth(user_credentials):
    # Sign up and log in to obtain a valid token
    client.post(
        "/v1/auth/signup",
        json=user_credentials,
    )
    login_response = client.post(
        "/v1/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    token = login_response.json().get("token")
    assert token is not None

    # Now, check authentication with the valid token
    response = client.post("/v1/auth/check", json={"token": token})
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


def test_logout(user_credentials):
    # Sign up and log in to obtain a valid token
    client.post(
        "/v1/auth/signup",
        json=user_credentials,
    )
    login_response = client.post(
        "/v1/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    token = login_response.json().get("token")
    assert token is not None

    # Logout using the valid token
    response = client.post("/v1/auth/logout", json={"token": token})
    assert response.status_code == 200
    assert response.json() == {"message": "Successfull"}

    # Optionally, verify that the session is invalidated
    check_response = client.post("/v1/auth/check", json={"token": token})
    assert check_response.status_code == 401
