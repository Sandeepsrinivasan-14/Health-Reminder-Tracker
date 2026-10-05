from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db, get_user_or_404
from ..models import User, VitalReading, utcnow
from ..risk import assess_reading
from ..schemas import Assessment, VitalCreate, VitalOut

router = APIRouter(tags=["vitals"])


def latest_vitals(db: Session, user_id: int, limit: int) -> list[VitalReading]:
    stmt = (
        select(VitalReading)
        .where(VitalReading.user_id == user_id)
        .order_by(VitalReading.recorded_at.desc(), VitalReading.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def assessment_for(user: User, reading: VitalReading) -> Assessment:
    return assess_reading(
        systolic=reading.systolic,
        diastolic=reading.diastolic,
        heart_rate=reading.heart_rate,
        blood_glucose=reading.blood_glucose,
        glucose_context=reading.glucose_context,
        weight_kg=reading.weight_kg,
        height_cm=user.height_cm,
    )


@router.get("/users/{user_id}/vitals", response_model=list[VitalOut])
def list_vitals(
    limit: int = Query(default=100, ge=1, le=1000),
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    return latest_vitals(db, user.id, limit)


@router.post("/users/{user_id}/vitals", response_model=VitalOut, status_code=status.HTTP_201_CREATED)
def create_vital(payload: VitalCreate, user: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["recorded_at"] = data["recorded_at"] or utcnow()
    reading = VitalReading(user_id=user.id, **data)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/users/{user_id}/assessment", response_model=Assessment)
def latest_assessment(user: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    readings = latest_vitals(db, user.id, 1)
    if not readings:
        raise HTTPException(status_code=404, detail="no readings logged for this patient")
    return assessment_for(user, readings[0])


@router.post("/assessment", response_model=Assessment)
def assess_ad_hoc(payload: VitalCreate, height_cm: float | None = Query(default=None, ge=50, le=250)):
    """Assess a reading without saving it."""
    return assess_reading(
        systolic=payload.systolic,
        diastolic=payload.diastolic,
        heart_rate=payload.heart_rate,
        blood_glucose=payload.blood_glucose,
        glucose_context=payload.glucose_context,
        weight_kg=payload.weight_kg,
        height_cm=height_cm,
    )


@router.delete("/vitals/{vital_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vital(vital_id: int, db: Session = Depends(get_db)):
    reading = db.get(VitalReading, vital_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="reading not found")
    db.delete(reading)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
