"""Pydantic request/response schemas with input validation."""

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

PHONE_RE = re.compile(r"^\+[1-9]\d{7,14}$")  # E.164
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _check_phone(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    value = value.replace(" ", "")
    if not PHONE_RE.match(value):
        raise ValueError("phone numbers must be in E.164 format, e.g. +919876543210")
    return value


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Users ----------


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    date_of_birth: date | None = None
    height_cm: float | None = Field(default=None, ge=50, le=250)
    caretaker_name: str | None = Field(default=None, max_length=120)
    caretaker_phone: str | None = None
    caretaker_email: EmailStr | None = None

    @field_validator("caretaker_phone")
    @classmethod
    def _phone(cls, value: str | None) -> str | None:
        return _check_phone(value)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    date_of_birth: date | None = None
    height_cm: float | None = Field(default=None, ge=50, le=250)
    caretaker_name: str | None = Field(default=None, max_length=120)
    caretaker_phone: str | None = None
    caretaker_email: EmailStr | None = None

    @field_validator("caretaker_phone")
    @classmethod
    def _phone(cls, value: str | None) -> str | None:
        return _check_phone(value)


class UserOut(ORMModel):
    id: int
    name: str
    email: str
    date_of_birth: date | None
    height_cm: float | None
    caretaker_name: str | None
    caretaker_phone: str | None
    caretaker_email: str | None
    created_at: datetime

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def _to_date(cls, value):
        return value.date() if isinstance(value, datetime) else value


# ---------- Vitals ----------


class VitalCreate(BaseModel):
    systolic: int = Field(ge=60, le=260, description="mmHg")
    diastolic: int = Field(ge=30, le=160, description="mmHg")
    heart_rate: int = Field(ge=25, le=250, description="beats per minute, at rest")
    blood_glucose: int = Field(ge=20, le=600, description="mg/dL")
    glucose_context: Literal["fasting", "random", "post_meal"] = "fasting"
    weight_kg: float = Field(ge=2, le=350)
    notes: str | None = Field(default=None, max_length=1000)
    recorded_at: datetime | None = None

    @model_validator(mode="after")
    def _systolic_above_diastolic(self):
        if self.systolic <= self.diastolic:
            raise ValueError("systolic pressure must be higher than diastolic pressure")
        return self


class VitalOut(ORMModel):
    id: int
    user_id: int
    systolic: int
    diastolic: int
    heart_rate: int
    blood_glucose: int
    glucose_context: str
    weight_kg: float
    notes: str | None
    recorded_at: datetime


# ---------- Risk assessment ----------


class Finding(BaseModel):
    metric: str
    value: str
    category: str
    severity: Literal["normal", "watch", "high", "urgent"]
    advice: str


class Assessment(BaseModel):
    overall: Literal["normal", "watch", "high", "urgent"]
    findings: list[Finding]
    bmi: float | None = None
    disclaimer: str


# ---------- Medications ----------


class MedicationBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    dosage: str = Field(min_length=1, max_length=60)
    schedule_time: str = Field(description="HH:MM, 24-hour, patient's local time")
    category: str = Field(default="Other", max_length=40)
    stock: int = Field(default=30, ge=0, le=10000)
    low_stock_threshold: int = Field(default=5, ge=0, le=1000)
    active: bool = True

    @field_validator("schedule_time")
    @classmethod
    def _check_time(cls, value: str) -> str:
        if not TIME_RE.match(value):
            raise ValueError("schedule_time must be HH:MM (24-hour)")
        return value


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    dosage: str | None = Field(default=None, min_length=1, max_length=60)
    schedule_time: str | None = None
    category: str | None = Field(default=None, max_length=40)
    stock: int | None = Field(default=None, ge=0, le=10000)
    low_stock_threshold: int | None = Field(default=None, ge=0, le=1000)
    active: bool | None = None

    @field_validator("schedule_time")
    @classmethod
    def _check_time(cls, value: str | None) -> str | None:
        if value is not None and not TIME_RE.match(value):
            raise ValueError("schedule_time must be HH:MM (24-hour)")
        return value


class MedicationOut(ORMModel):
    id: int
    user_id: int
    name: str
    dosage: str
    schedule_time: str
    category: str
    stock: int
    low_stock_threshold: int
    active: bool
    low_stock: bool = False
    status_today: Literal["pending", "taken", "skipped"] = "pending"


class DoseCreate(BaseModel):
    status: Literal["taken", "skipped"]


class DoseOut(ORMModel):
    id: int
    medication_id: int
    status: str
    logged_at: datetime


# ---------- Alerts ----------


class ReminderRequest(BaseModel):
    channel: Literal["sms", "whatsapp", "email"] = "sms"


class SOSRequest(BaseModel):
    message: str | None = Field(default=None, max_length=500)
    channels: list[Literal["sms", "whatsapp", "email"]] = ["sms", "email"]


class AlertOut(ORMModel):
    id: int
    user_id: int
    kind: str
    channel: str
    status: str
    detail: str | None
    created_at: datetime


# ---------- AI ----------


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    source: Literal["llm", "rules"]
    disclaimer: str


class TipsResponse(BaseModel):
    tips: list[str]
    source: Literal["llm", "rules"]


class StatusOut(BaseModel):
    status: str
    version: str
    database: str
    llm: bool
    sms: bool
    email: bool
