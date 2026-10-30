import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_students.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_db)
    database.init_db()
    with TestClient(app) as test_client:
        yield test_client


def sample_student(student_id="STU001"):
    return {
        "student_id": student_id,
        "name": "Riya Das",
        "date_of_birth": "2005-04-12",
        "email": "riya@example.com",
        "phone": "9876543210",
        "course": "BCA",
        "address": "Kolkata",
        "enrollment_date": "2024-08-01",
    }


def test_crud_flow(client):
    response = client.post("/students", json=sample_student())
    assert response.status_code == 201
    assert response.json()["student_id"] == "STU001"

    assert client.get("/students").status_code == 200
    assert client.get("/students/STU001").json()["name"] == "Riya Das"

    response = client.patch("/students/STU001", json={"course": "MCA"})
    assert response.status_code == 200
    assert response.json()["course"] == "MCA"

    assert client.delete("/students/STU001").status_code == 204
    assert client.get("/students/STU001").status_code == 404


def test_duplicate_student_id_returns_409(client):
    client.post("/students", json=sample_student())
    response = client.post("/students", json=sample_student())
    assert response.status_code == 409


def test_missing_contact_is_rejected(client):
    data = sample_student()
    data["email"] = None
    data["phone"] = None
    response = client.post("/students", json=data)
    assert response.status_code == 422


def test_filter_by_course(client):
    client.post("/students", json=sample_student())
    response = client.get("/students?course=BCA")
    assert response.status_code == 200
    assert len(response.json()) == 1
