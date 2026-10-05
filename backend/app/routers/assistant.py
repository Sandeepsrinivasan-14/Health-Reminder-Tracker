from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_assistant, get_db, get_user_or_404
from ..models import User
from ..risk import DISCLAIMER
from ..schemas import ChatRequest, ChatResponse, TipsResponse, VitalOut
from ..services.assistant import HealthAssistant
from .vitals import assessment_for, latest_vitals

router = APIRouter(prefix="/users/{user_id}/assistant", tags=["assistant"])


def _context(db: Session, user: User):
    readings = latest_vitals(db, user.id, 5)
    as_dicts = [VitalOut.model_validate(r).model_dump(mode="json") for r in readings]
    assessment = assessment_for(user, readings[0]) if readings else None
    return as_dicts, assessment


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    assistant: HealthAssistant = Depends(get_assistant),
):
    readings, assessment = _context(db, user)
    answer, source = assistant.answer(payload.question, readings, assessment)
    return ChatResponse(answer=answer, source=source, disclaimer=DISCLAIMER)


@router.get("/tips", response_model=TipsResponse)
def tips(
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    assistant: HealthAssistant = Depends(get_assistant),
):
    readings, assessment = _context(db, user)
    items, source = assistant.tips(readings, assessment)
    return TipsResponse(tips=items, source=source)
