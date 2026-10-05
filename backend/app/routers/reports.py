import re

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db, get_user_or_404
from ..models import Medication, User
from ..services.reports import patient_pdf, vitals_csv
from .vitals import latest_vitals

router = APIRouter(prefix="/users/{user_id}/reports", tags=["reports"])


def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "patient"


@router.get("/pdf", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def pdf_report(user: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    vitals = latest_vitals(db, user.id, 100)
    meds = list(db.scalars(select(Medication).where(Medication.user_id == user.id)))
    return Response(
        content=patient_pdf(user, vitals, meds),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_slug(user.name)}_health_report.pdf"'},
    )


@router.get("/csv", response_class=Response, responses={200: {"content": {"text/csv": {}}}})
def csv_report(user: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    vitals = latest_vitals(db, user.id, 1000)
    return Response(
        content=vitals_csv(vitals),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{_slug(user.name)}_vitals.csv"'},
    )
