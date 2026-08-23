import pytest
from fastapi.testclient import TestClient

from database import SessionLocal
from models import Candidate, Application
from main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    db = SessionLocal()

    try:
        db.query(Application).delete()
        db.query(Candidate).delete()
        db.commit()

        yield

    finally:
        db.close()


def test_create_candidate():
    response = client.post(
        "/candidates",
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
    response = client.get("/candidates")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_candidate():
    create_response = client.post(
        "/candidates",
        json={
            "name": "Get Test",
            "email": "get@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.get(f"/candidates/{candidate_id}")

    assert response.status_code == 200
    assert response.json()["id"] == candidate_id


def test_update_candidate():
    create_response = client.post(
        "/candidates",
        json={
            "name": "Update Test",
            "email": "update@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.put(
        f"/candidates/{candidate_id}",
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
    create_response = client.post(
        "/candidates",
        json={
            "name": "Delete Test",
            "email": "delete@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.delete(f"/candidates/{candidate_id}")

    assert response.status_code == 200

    get_response = client.get(f"/candidates/{candidate_id}")

    assert get_response.status_code == 404


def test_invalid_candidate_data():
    response = client.post(
        "/candidates",
        json={
            "name": "Invalid User",
            "email": "not-an-email",
            "phone": "123",
        },
    )

    assert response.status_code == 422


def test_invalid_nigerian_phone_number():
    response = client.post(
        "/candidates",
        json={
            "name": "Invalid Phone",
            "email": "invalidphone@gmail.com",
            "phone": "12345678901",
        },
    )

    assert response.status_code == 422


def test_id_is_not_reused_after_deletion():
    first_response = client.post(
        "/candidates",
        json={
            "name": "First Candidate",
            "email": "first@gmail.com",
            "phone": "08012345678",
        },
    )

    first_id = first_response.json()["id"]

    second_response = client.post(
        "/candidates",
        json={
            "name": "Second Candidate",
            "email": "second@gmail.com",
            "phone": "08112345678",
        },
    )

    second_id = second_response.json()["id"]

    client.delete(f"/candidates/{first_id}")

    third_response = client.post(
        "/candidates",
        json={
            "name": "Third Candidate",
            "email": "third@gmail.com",
            "phone": "09012345678",
        },
    )

    third_id = third_response.json()["id"]

    assert third_id > second_id


def test_get_missing_candidate():
    response = client.get("/candidates/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"


def test_update_candidate_with_invalid_data():
    create_response = client.post(
        "/candidates",
        json={
            "name": "Update Test",
            "email": "update@example.com",
            "phone": "08012345678",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.put(
        f"/candidates/{candidate_id}",
        json={
            "name": "Invalid Update",
            "email": "not-an-email",
            "phone": "123",
        },
    )

    assert response.status_code == 422