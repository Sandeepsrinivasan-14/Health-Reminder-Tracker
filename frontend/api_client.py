"""Thin, typed wrapper around the Health Reminder Tracker REST API."""

from __future__ import annotations

import os
from typing import Any

import httpx


class APIError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _detail(resp: httpx.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text or resp.reason_phrase
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if isinstance(detail, list):  # FastAPI validation errors
        return "; ".join(f"{'.'.join(str(p) for p in d.get('loc', [])[1:])}: {d.get('msg')}" for d in detail)
    return str(detail)


class HealthAPI:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, transport: httpx.BaseTransport | None = None):
        base_url = (base_url or os.getenv("API_URL", "http://127.0.0.1:8000")).rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"  # Render's fromService host property has no scheme
        key = api_key if api_key is not None else os.getenv("API_KEY", "")
        headers = {"X-API-Key": key} if key else {}
        self.base_url = base_url
        self._client = httpx.Client(base_url=f"{base_url}", headers=headers, timeout=30, transport=transport)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        resp = self._client.request(method, path, **kwargs)
        if resp.status_code >= 400:
            raise APIError(resp.status_code, _detail(resp))
        if resp.status_code == 204:
            return None
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.content

    # meta
    def health(self) -> dict:
        return self._request("GET", "/health")

    # patients
    def list_users(self) -> list[dict]:
        return self._request("GET", "/api/v1/users")

    def create_user(self, **data) -> dict:
        return self._request("POST", "/api/v1/users", json=data)

    def update_user(self, user_id: int, **data) -> dict:
        return self._request("PATCH", f"/api/v1/users/{user_id}", json=data)

    def delete_user(self, user_id: int) -> None:
        self._request("DELETE", f"/api/v1/users/{user_id}")

    # vitals
    def list_vitals(self, user_id: int, limit: int = 200) -> list[dict]:
        return self._request("GET", f"/api/v1/users/{user_id}/vitals", params={"limit": limit})

    def add_vital(self, user_id: int, **data) -> dict:
        return self._request("POST", f"/api/v1/users/{user_id}/vitals", json=data)

    def delete_vital(self, vital_id: int) -> None:
        self._request("DELETE", f"/api/v1/vitals/{vital_id}")

    def assessment(self, user_id: int) -> dict | None:
        try:
            return self._request("GET", f"/api/v1/users/{user_id}/assessment")
        except APIError as exc:
            if exc.status == 404:
                return None
            raise

    # medications
    def list_medications(self, user_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/users/{user_id}/medications")

    def add_medication(self, user_id: int, **data) -> dict:
        return self._request("POST", f"/api/v1/users/{user_id}/medications", json=data)

    def update_medication(self, med_id: int, **data) -> dict:
        return self._request("PATCH", f"/api/v1/medications/{med_id}", json=data)

    def delete_medication(self, med_id: int) -> None:
        self._request("DELETE", f"/api/v1/medications/{med_id}")

    def log_dose(self, med_id: int, status: str) -> dict:
        return self._request("POST", f"/api/v1/medications/{med_id}/doses", json={"status": status})

    def remind(self, med_id: int, channel: str) -> dict:
        return self._request("POST", f"/api/v1/medications/{med_id}/remind", json={"channel": channel})

    # alerts
    def sos(self, user_id: int, channels: list[str] | None = None) -> list[dict]:
        return self._request("POST", f"/api/v1/users/{user_id}/sos", json={"channels": channels or ["sms", "email"]})

    def list_alerts(self, user_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/users/{user_id}/alerts")

    # assistant
    def chat(self, user_id: int, question: str) -> dict:
        return self._request("POST", f"/api/v1/users/{user_id}/assistant/chat", json={"question": question})

    def tips(self, user_id: int) -> dict:
        return self._request("GET", f"/api/v1/users/{user_id}/assistant/tips")

    # reports
    def report_pdf(self, user_id: int) -> bytes:
        return self._request("GET", f"/api/v1/users/{user_id}/reports/pdf")

    def report_csv(self, user_id: int) -> bytes:
        return self._request("GET", f"/api/v1/users/{user_id}/reports/csv")
