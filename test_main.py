from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


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
    # Create a candidate first
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

    # Confirm candidate no longer exists
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