"""FastAPI dependencies: settings, DB sessions, API-key auth and shared services."""

import secrets
from collections.abc import Iterator

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from .config import Settings
from .models import Medication, User
from .services.assistant import HealthAssistant
from .services.notifications import Notifier

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings


def get_db(request: Request) -> Iterator[Session]:
    yield from request.app.state.db.session()


def require_api_key(
    key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings_dep),
) -> None:
    if not settings.api_key:  # auth disabled (local development)
        return
    if not key or not secrets.compare_digest(key, settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")


def get_assistant(request: Request) -> HealthAssistant:
    return request.app.state.assistant


def get_notifier(request: Request) -> Notifier:
    return request.app.state.notifier


def get_user_or_404(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="patient not found")
    return user


def get_medication_or_404(medication_id: int, db: Session = Depends(get_db)) -> Medication:
    med = db.get(Medication, medication_id)
    if med is None:
        raise HTTPException(status_code=404, detail="medication not found")
    return med
