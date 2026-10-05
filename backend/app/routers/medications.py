from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings
from ..deps import get_db, get_medication_or_404, get_settings_dep, get_user_or_404
from ..models import DoseLog, Medication, User, utcnow
from ..schemas import DoseCreate, DoseOut, MedicationCreate, MedicationOut, MedicationUpdate

router = APIRouter(tags=["medications"])


def _today_bounds(tz: ZoneInfo, now: datetime | None = None) -> tuple[datetime, datetime]:
    local_now = (now or utcnow()).astimezone(tz)
    start = datetime.combine(local_now.date(), time.min, tzinfo=tz)
    return start, start + timedelta(days=1)


def _status_today(db: Session, med: Medication, tz: ZoneInfo) -> str:
    start, end = _today_bounds(tz)
    stmt = (
        select(DoseLog.status)
        .where(DoseLog.medication_id == med.id, DoseLog.logged_at >= start, DoseLog.logged_at < end)
        .order_by(DoseLog.logged_at.desc(), DoseLog.id.desc())
        .limit(1)
    )
    return db.scalar(stmt) or "pending"


def to_out(db: Session, med: Medication, tz: ZoneInfo) -> MedicationOut:
    out = MedicationOut.model_validate(med)
    out.low_stock = med.stock <= med.low_stock_threshold
    out.status_today = _status_today(db, med, tz)
    return out


@router.get("/users/{user_id}/medications", response_model=list[MedicationOut])
def list_medications(
    include_inactive: bool = False,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    stmt = select(Medication).where(Medication.user_id == user.id)
    if not include_inactive:
        stmt = stmt.where(Medication.active.is_(True))
    meds = db.scalars(stmt.order_by(Medication.schedule_time, Medication.name)).all()
    tz = ZoneInfo(settings.timezone)
    return [to_out(db, m, tz) for m in meds]


@router.post("/users/{user_id}/medications", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication(
    payload: MedicationCreate,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    med = Medication(user_id=user.id, **payload.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return to_out(db, med, ZoneInfo(settings.timezone))


@router.get("/users/{user_id}/medications/due", response_model=list[MedicationOut])
def due_medications(
    window_minutes: int = Query(default=30, ge=1, le=720),
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    """Active medications scheduled within +/- window_minutes of now with no dose logged today."""
    tz = ZoneInfo(settings.timezone)
    now = utcnow().astimezone(tz)
    now_minutes = now.hour * 60 + now.minute
    meds = db.scalars(select(Medication).where(Medication.user_id == user.id, Medication.active.is_(True))).all()
    due = []
    for med in meds:
        hh, mm = map(int, med.schedule_time.split(":"))
        if abs(now_minutes - (hh * 60 + mm)) <= window_minutes and _status_today(db, med, tz) == "pending":
            due.append(to_out(db, med, tz))
    return due


@router.patch("/medications/{medication_id}", response_model=MedicationOut)
def update_medication(
    payload: MedicationUpdate,
    med: Medication = Depends(get_medication_or_404),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(med, field, value)
    db.commit()
    db.refresh(med)
    return to_out(db, med, ZoneInfo(settings.timezone))


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(med: Medication = Depends(get_medication_or_404), db: Session = Depends(get_db)):
    db.delete(med)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/medications/{medication_id}/doses", response_model=DoseOut, status_code=status.HTTP_201_CREATED)
def log_dose(payload: DoseCreate, med: Medication = Depends(get_medication_or_404), db: Session = Depends(get_db)):
    if payload.status == "taken":
        if med.stock <= 0:
            raise HTTPException(status_code=409, detail="no stock left for this medication; update the stock after refilling")
        med.stock -= 1
    dose = DoseLog(medication_id=med.id, status=payload.status)
    db.add(dose)
    db.commit()
    db.refresh(dose)
    return dose


@router.get("/medications/{medication_id}/doses", response_model=list[DoseOut])
def list_doses(
    limit: int = Query(default=50, ge=1, le=500),
    med: Medication = Depends(get_medication_or_404),
    db: Session = Depends(get_db),
):
    stmt = select(DoseLog).where(DoseLog.medication_id == med.id).order_by(DoseLog.logged_at.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.delete("/doses/{dose_id}", status_code=status.HTTP_204_NO_CONTENT)
def undo_dose(dose_id: int, db: Session = Depends(get_db)):
    dose = db.get(DoseLog, dose_id)
    if dose is None:
        raise HTTPException(status_code=404, detail="dose not found")
    if dose.status == "taken":
        dose.medication.stock += 1
    db.delete(dose)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
