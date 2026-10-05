"""End-to-end smoke tests: the real Streamlit app talking to a real (in-process) API server."""

import socket
import sys
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "frontend"))

from app.config import Settings  # noqa: E402
from app.database import Database  # noqa: E402
from app.main import create_app  # noqa: E402

APP_FILE = str(ROOT / "frontend" / "streamlit_app.py")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def api_url():
    settings = Settings(_env_file=None, database_url="sqlite://", api_key="test-key")
    app = create_app(settings, Database(settings.database_url))
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def env(api_url, monkeypatch):
    monkeypatch.setenv("API_URL", api_url)
    monkeypatch.setenv("API_KEY", "test-key")


def test_api_client_roundtrip(env):
    from api_client import APIError, HealthAPI

    api = HealthAPI()
    user = api.create_user(name="Client Test", email="client@example.com")
    api.add_vital(
        user["id"], systolic=150, diastolic=95, heart_rate=70, blood_glucose=100, glucose_context="fasting", weight_kg=70
    )
    assert api.assessment(user["id"])["overall"] == "high"
    with pytest.raises(APIError) as err:
        api.create_user(name="Client Test", email="client@example.com")
    assert err.value.status == 409
    with pytest.raises(APIError) as err:
        HealthAPI(api_key="wrong").list_users()
    assert err.value.status == 401


def test_empty_state_then_dashboard(env):
    from api_client import HealthAPI

    at = AppTest.from_file(APP_FILE, default_timeout=30).run()
    assert not at.exception
    assert any("Health Reminder" in t.value for t in at.sidebar.title)

    HealthAPI().create_user(name="Asha Verma", email="asha@example.com", height_cm=160)
    at = AppTest.from_file(APP_FILE, default_timeout=30).run()
    assert not at.exception
    assert any("Log a new reading" in e.label for e in at.expander)


@pytest.mark.parametrize("page", ["💊 Medications", "🤖 Assistant", "📄 Reports", "⚙️ Patient settings"])
def test_every_page_renders(env, page):
    at = AppTest.from_file(APP_FILE, default_timeout=30).run()
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, at.exception
