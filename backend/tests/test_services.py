import httpx

from app.config import Settings
from app.risk import assess_reading
from app.services.assistant import HealthAssistant
from app.services.notifications import Notifier


def _settings(**kw) -> Settings:
    kw.setdefault("database_url", "sqlite://")
    return Settings(_env_file=None, **kw)


def test_postgres_url_is_normalised():
    assert _settings(database_url="postgres://u:p@h/db").database_url.startswith("postgresql+psycopg://")


def test_llm_answer_is_grounded_and_falls_back():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = request.read().decode()
        seen["auth"] = request.headers["authorization"]
        return httpx.Response(200, json={"choices": [{"message": {"content": "Your BP is high."}}]})

    assistant = HealthAssistant(_settings(groq_api_key="k"), client=httpx.Client(transport=httpx.MockTransport(handler)))
    assessment = assess_reading(
        systolic=150, diastolic=95, heart_rate=70, blood_glucose=90, glucose_context="fasting", weight_kg=70
    )
    readings = [
        {
            "recorded_at": "2026-01-01",
            "systolic": 150,
            "diastolic": 95,
            "heart_rate": 70,
            "blood_glucose": 90,
            "glucose_context": "fasting",
            "weight_kg": 70,
        }
    ]
    answer, source = assistant.answer("bp?", readings, assessment)
    assert (answer, source) == ("Your BP is high.", "llm")
    assert "Stage 2 hypertension range" in seen["body"]
    assert "Never diagnose" in seen["body"]
    assert seen["auth"] == "Bearer k"

    failing = HealthAssistant(
        _settings(groq_api_key="k"),
        client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))),
    )
    answer, source = failing.answer("bp?", readings, assessment)
    assert source == "rules"
    assert "Stage 2" in answer


def test_twilio_sms_and_whatsapp():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(201, json={"sid": "SM123"})

    settings = _settings(twilio_account_sid="AC1", twilio_auth_token="t", twilio_from_number="+15550000000")
    notifier = Notifier(settings, http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert notifier.send_message("sms", "+919876543210", "hi").status == "sent"
    result = notifier.send_message("whatsapp", "+919876543210", "hi")
    assert result.status == "sent" and result.detail == "SM123"
    assert b"whatsapp%3A%2B919876543210" in calls[1].read()
    assert notifier.send_message("sms", None, "hi").status == "failed"


def test_twilio_error_is_reported():
    handler = lambda r: httpx.Response(400, json={"message": "invalid number"})  # noqa: E731
    settings = _settings(twilio_account_sid="AC1", twilio_auth_token="t", twilio_from_number="+15550000000")
    notifier = Notifier(settings, http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    result = notifier.send_message("sms", "+919876543210", "hi")
    assert result.status == "failed"
    assert "invalid number" in result.detail


class FakeSMTP:
    sent = []

    def __init__(self, host, port, timeout):
        self.host = host

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        assert password == "pw"

    def send_message(self, msg):
        FakeSMTP.sent.append(msg)


def test_email():
    settings = _settings(smtp_username="me@example.com", smtp_password="pw")
    notifier = Notifier(settings, smtp_factory=FakeSMTP)
    assert notifier.send_email("care@example.com", "Subject", "Body").status == "sent"
    assert FakeSMTP.sent[-1]["To"] == "care@example.com"
    assert Notifier(_settings()).send_email("care@example.com", "s", "b").status == "not_configured"
