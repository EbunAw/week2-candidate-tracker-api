import pytest
from fastapi.testclient import TestClient

from auth import hash_password
from database import SessionLocal
from models import Candidate, Application, User
from main import app


client = TestClient(app)

def get_auth_headers():
    response = client.post(
        "/login",
        data={
            "username": "oregeorge",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture(autouse=True)
def clean_database():
    db = SessionLocal()

    try:
        db.query(Application).delete()
        db.query(Candidate).delete()
        db.query(User).delete()
        db.commit()

        test_user = User(
            username="oregeorge",
            password_hash=hash_password("TestPassword123!")
        )

        db.add(test_user)
        db.commit()

        yield

    finally:
        db.close()


def test_create_candidate():
    headers = get_auth_headers()

    response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "08012345678",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "08012345678"
    assert "id" in data


def test_get_candidates():
    headers = get_auth_headers()

    response = client.get(
        "/candidates",
        headers=headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_candidate():
    headers = get_auth_headers()

    create_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Get Test",
            "email": "get@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.get(
        f"/candidates/{candidate_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == candidate_id

def test_update_candidate():
    headers = get_auth_headers()

    create_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Update Test",
            "email": "update@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.put(
        f"/candidates/{candidate_id}",
        headers=headers,
        json={
            "name": "Updated User",
            "email": "updated@example.com",
            "phone": "08099999999",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"
    assert response.json()["email"] == "updated@example.com"
    assert response.json()["phone"] == "08099999999"


def test_delete_candidate():
    headers = get_auth_headers()

    create_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Delete Test",
            "email": "delete@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.delete(
        f"/candidates/{candidate_id}",
        headers=headers,
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/candidates/{candidate_id}",
        headers=headers,
    )

    assert get_response.status_code == 404

def test_invalid_candidate_data():
    headers = get_auth_headers()

    response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Invalid User",
            "email": "not-an-email",
            "phone": "123",
        },
    )

    assert response.status_code == 422


def test_invalid_nigerian_phone_number():
    headers = get_auth_headers()

    response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Invalid Phone",
            "email": "invalidphone@gmail.com",
            "phone": "12345678901",
        },
    )

    assert response.status_code == 422


def test_id_is_not_reused_after_deletion():
    headers = get_auth_headers()

    first_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "First Candidate",
            "email": "first@gmail.com",
            "phone": "08012345678",
        },
    )

    first_id = first_response.json()["id"]

    second_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Second Candidate",
            "email": "second@gmail.com",
            "phone": "08112345678",
        },
    )

    second_id = second_response.json()["id"]

    client.delete(
        f"/candidates/{first_id}",
        headers=headers,
    )

    third_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Third Candidate",
            "email": "third@gmail.com",
            "phone": "09012345678",
        },
    )

    third_id = third_response.json()["id"]

    assert third_id > second_id


def test_get_missing_candidate():
    headers = get_auth_headers()

    response = client.get(
        "/candidates/999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"

def test_update_candidate_with_invalid_data():
    headers = get_auth_headers()

    create_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Update Test",
            "email": "update@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.put(
        f"/candidates/{candidate_id}",
        headers=headers,
        json={
            "name": "Invalid Update",
            "email": "not-an-email",
            "phone": "123",
        },
    )

    assert response.status_code == 422


def test_create_application_for_candidate():
    headers = get_auth_headers()

    candidate_response = client.post(
        "/candidates",
        headers=headers,
        json={
            "name": "Application Test",
            "email": "application@example.com",
            "phone": "08012345678",
        },
    )

    assert candidate_response.status_code == 200

    candidate_id = candidate_response.json()["id"]

    application_response = client.post(
        "/applications",
        headers=headers,
        json={
            "candidate_id": candidate_id,
            "position": "Python Developer",
            "status": "Applied",
        },
    )

    assert application_response.status_code == 200

    application_data = application_response.json()

    assert application_data["candidate_id"] == candidate_id
    assert application_data["position"] == "Python Developer"
    assert application_data["status"] == "Applied"
    assert "id" in application_data

    application_id = application_data["id"]

    get_response = client.get(
        f"/applications/{application_id}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == application_id
    assert get_response.json()["candidate_id"] == candidate_id

def test_protected_endpoint_requires_authentication():
    response = client.get("/candidates")

    assert response.status_code == 401

def test_login_rate_limit():
    for _ in range(5):
        response = client.post(
            "/login",
            data={
                "username": "oregeorge",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    response = client.post(
        "/login",
        data={
            "username": "oregeorge",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 429

def test_sensitive_data_is_masked():
    from logging_config import mask_sensitive_data

    data = {
        "username": "oregeorge",
        "password": "TestPassword123!",
        "password_hash": "$argon2id$example",
        "access_token": "secret-token",
        "nin": "12345678901",
        "bvn": "12345678901",
        "card_number": "4111111111111111",
    }

    masked = mask_sensitive_data(data)

    assert masked["username"] == "oregeorge"
    assert masked["password"] == "***"
    assert masked["password_hash"] == "***"
    assert masked["access_token"] == "***"
    assert masked["nin"] == "***"
    assert masked["bvn"] == "***"
    assert masked["card_number"] == "***"

def test_global_exception_handler():
    from main import global_exception_handler
    from starlette.requests import Request

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test-error",
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 1234),
        }
    )

    response = __import__("asyncio").run(
        global_exception_handler(
            request,
            Exception("database password=secret123")
        )
    )

    assert response.status_code == 500

    body = response.body.decode()

    assert "An unexpected error occurred." in body
    assert "secret123" not in body
    assert "password" not in body