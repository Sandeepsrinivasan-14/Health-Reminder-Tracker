from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db, get_medication_or_404, get_notifier, get_user_or_404
from ..models import AlertLog, Medication, User
from ..schemas import AlertOut, ReminderRequest, SOSRequest
from ..services.notifications import NotificationResult, Notifier

router = APIRouter(tags=["alerts"])


def _log(db: Session, user: User, kind: str, result: NotificationResult) -> AlertLog:
    entry = AlertLog(user_id=user.id, kind=kind, channel=result.channel, status=result.status, detail=result.detail)
    db.add(entry)
    return entry


@router.post("/users/{user_id}/sos", response_model=list[AlertOut])
def send_sos(
    payload: SOSRequest,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier),
):
    body = payload.message or (
        f"EMERGENCY: {user.name} pressed the SOS button in Health Reminder Tracker and may need help right away."
    )
    entries = []
    for channel in dict.fromkeys(payload.channels):  # de-duplicate, keep order
        result = notifier.send(
            channel, to_phone=user.caretaker_phone, to_email=user.caretaker_email, subject=f"SOS alert for {user.name}", body=body
        )
        entries.append(_log(db, user, "sos", result))
    db.commit()
    for e in entries:
        db.refresh(e)
    return entries


@router.post("/medications/{medication_id}/remind", response_model=AlertOut)
def send_reminder(
    payload: ReminderRequest,
    med: Medication = Depends(get_medication_or_404),
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier),
):
    user = med.user
    body = f"Reminder: {user.name} should take {med.name} {med.dosage} (scheduled {med.schedule_time})."
    result = notifier.send(
        payload.channel,
        to_phone=user.caretaker_phone,
        to_email=user.caretaker_email,
        subject=f"Medication reminder: {med.name}",
        body=body,
    )
    entry = _log(db, user, "reminder", result)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/users/{user_id}/alerts", response_model=list[AlertOut])
def list_alerts(
    limit: int = Query(default=50, ge=1, le=500),
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    stmt = (
        select(AlertLog).where(AlertLog.user_id == user.id).order_by(AlertLog.created_at.desc(), AlertLog.id.desc()).limit(limit)
    )
    return db.scalars(stmt).all()
