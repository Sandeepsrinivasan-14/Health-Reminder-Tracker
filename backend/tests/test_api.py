from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.config import Settings
from app.database import Database
from app.main import create_app

from .conftest import NORMAL_READING


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["llm"] is False


def test_user_crud(client, patient):
    assert client.get("/api/v1/users").json()[0]["email"] == "test@example.com"
    dup = client.post("/api/v1/users", json={"name": "Again", "email": "test@example.com"})
    assert dup.status_code == 409

    upd = client.patch(f"/api/v1/users/{patient['id']}", json={"name": "Renamed"})
    assert upd.json()["name"] == "Renamed"

    assert client.delete(f"/api/v1/users/{patient['id']}").status_code == 204
    assert client.get(f"/api/v1/users/{patient['id']}").status_code == 404


def test_user_validation(client):
    bad_email = client.post("/api/v1/users", json={"name": "X", "email": "not-an-email"})
    assert bad_email.status_code == 422
    bad_phone = client.post("/api/v1/users", json={"name": "X", "email": "x@example.com", "caretaker_phone": "12345"})
    assert bad_phone.status_code == 422


def test_vitals_and_assessment(client, patient):
    uid = patient["id"]
    assert client.get(f"/api/v1/users/{uid}/assessment").status_code == 404

    r = client.post(f"/api/v1/users/{uid}/vitals", json=NORMAL_READING)
    assert r.status_code == 201
    high = dict(NORMAL_READING, systolic=150, diastolic=95, blood_glucose=140)
    client.post(f"/api/v1/users/{uid}/vitals", json=high)

    readings = client.get(f"/api/v1/users/{uid}/vitals").json()
    assert len(readings) == 2
    assert readings[0]["systolic"] == 150  # newest first
    assert readings[0]["recorded_at"].endswith("Z") or "+00:00" in readings[0]["recorded_at"]

    assessment = client.get(f"/api/v1/users/{uid}/assessment").json()
    assert assessment["overall"] == "high"
    assert assessment["bmi"] == 24.2


def test_vitals_validation(client, patient):
    uid = patient["id"]
    impossible = dict(NORMAL_READING, systolic=70, diastolic=90)
    assert client.post(f"/api/v1/users/{uid}/vitals", json=impossible).status_code == 422
    out_of_range = dict(NORMAL_READING, heart_rate=400)
    assert client.post(f"/api/v1/users/{uid}/vitals", json=out_of_range).status_code == 422
    assert client.post("/api/v1/users/999/vitals", json=NORMAL_READING).status_code == 404


def test_medication_lifecycle(client, patient):
    uid = patient["id"]
    med = client.post(
        f"/api/v1/users/{uid}/medications",
        json={
            "name": "Metformin",
            "dosage": "500 mg",
            "schedule_time": "08:00",
            "category": "Diabetes",
            "stock": 1,
            "low_stock_threshold": 5,
        },
    ).json()
    assert med["status_today"] == "pending"
    assert med["low_stock"] is True

    dose = client.post(f"/api/v1/medications/{med['id']}/doses", json={"status": "taken"})
    assert dose.status_code == 201
    meds = client.get(f"/api/v1/users/{uid}/medications").json()
    assert meds[0]["stock"] == 0
    assert meds[0]["status_today"] == "taken"

    # Out of stock: taking another dose is refused
    assert client.post(f"/api/v1/medications/{med['id']}/doses", json={"status": "taken"}).status_code == 409

    # Undo restores the stock
    assert client.delete(f"/api/v1/doses/{dose.json()['id']}").status_code == 204
    assert client.get(f"/api/v1/users/{uid}/medications").json()[0]["stock"] == 1

    upd = client.patch(f"/api/v1/medications/{med['id']}", json={"stock": 30, "schedule_time": "21:15"})
    assert upd.json()["schedule_time"] == "21:15"
    assert upd.json()["low_stock"] is False
    assert client.patch(f"/api/v1/medications/{med['id']}", json={"schedule_time": "25:00"}).status_code == 422

    assert client.delete(f"/api/v1/medications/{med['id']}").status_code == 204
    assert client.get(f"/api/v1/users/{uid}/medications").json() == []


def test_due_medications(client, patient):
    uid = patient["id"]
    now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%H:%M")
    med = client.post(f"/api/v1/users/{uid}/medications", json={"name": "Any", "dosage": "1", "schedule_time": now}).json()
    due = client.get(f"/api/v1/users/{uid}/medications/due", params={"window_minutes": 5}).json()
    assert [m["id"] for m in due] == [med["id"]]
    client.post(f"/api/v1/medications/{med['id']}/doses", json={"status": "skipped"})
    assert client.get(f"/api/v1/users/{uid}/medications/due", params={"window_minutes": 5}).json() == []


def test_sos_without_credentials_is_logged_not_crashed(client, patient):
    resp = client.post(f"/api/v1/users/{patient['id']}/sos", json={})
    assert resp.status_code == 200
    statuses = {a["channel"]: a["status"] for a in resp.json()}
    assert statuses == {"sms": "not_configured", "email": "not_configured"}
    assert len(client.get(f"/api/v1/users/{patient['id']}/alerts").json()) == 2


def test_assistant_rule_based(client, patient):
    uid = patient["id"]
    empty = client.post(f"/api/v1/users/{uid}/assistant/chat", json={"question": "How is my BP?"}).json()
    assert empty["source"] == "rules"
    assert "don't have any readings" in empty["answer"]

    client.post(f"/api/v1/users/{uid}/vitals", json=dict(NORMAL_READING, systolic=150, diastolic=95))
    chat = client.post(f"/api/v1/users/{uid}/assistant/chat", json={"question": "Is my blood pressure ok?"}).json()
    assert "Stage 2" in chat["answer"]
    assert "Blood glucose" not in chat["answer"]  # answer is scoped to the question

    tips = client.get(f"/api/v1/users/{uid}/assistant/tips").json()
    assert len(tips["tips"]) == 5


def test_reports(client, patient):
    uid = patient["id"]
    client.post(f"/api/v1/users/{uid}/vitals", json=NORMAL_READING)
    client.post(f"/api/v1/users/{uid}/medications", json={"name": "Aspirin", "dosage": "75 mg", "schedule_time": "09:00"})
    pdf = client.get(f"/api/v1/users/{uid}/reports/pdf")
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    csv = client.get(f"/api/v1/users/{uid}/reports/csv")
    assert csv.text.splitlines()[0].startswith("recorded_at,systolic")
    assert len(csv.text.splitlines()) == 2


def test_api_key_required_when_configured():
    settings = Settings(_env_file=None, database_url="sqlite://", api_key="s3cret")
    app = create_app(settings, Database(settings.database_url))
    with TestClient(app) as c:
        assert c.get("/health").status_code == 200  # health stays public
        assert c.get("/api/v1/users").status_code == 401
        assert c.get("/api/v1/users", headers={"X-API-Key": "wrong"}).status_code == 401
        assert c.get("/api/v1/users", headers={"X-API-Key": "s3cret"}).status_code == 200
