import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import Database
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, environment="test", database_url="sqlite://", cors_origins="http://testserver")


@pytest.fixture
def client(settings):
    app = create_app(settings, Database(settings.database_url))
    with TestClient(app) as c:
        yield c


@pytest.fixture
def patient(client):
    resp = client.post(
        "/api/v1/users",
        json={
            "name": "Test Patient",
            "email": "test@example.com",
            "height_cm": 170,
            "caretaker_phone": "+919876543210",
            "caretaker_email": "care@example.com",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


NORMAL_READING = {
    "systolic": 118,
    "diastolic": 76,
    "heart_rate": 72,
    "blood_glucose": 92,
    "glucose_context": "fasting",
    "weight_kg": 70,
}
