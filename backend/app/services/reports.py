"""Patient report generation (PDF and CSV)."""

import csv
import io
from datetime import UTC, datetime

from fpdf import FPDF

from ..models import Medication, User, VitalReading
from ..risk import DISCLAIMER, METRIC_LABELS, assess_reading


def _latin1(text: str) -> str:
    # Core PDF fonts only support Latin-1; replace anything else instead of crashing.
    return text.encode("latin-1", "replace").decode("latin-1")


def vitals_csv(vitals: list[VitalReading]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["recorded_at", "systolic", "diastolic", "heart_rate", "blood_glucose", "glucose_context", "weight_kg", "notes"]
    )
    for v in vitals:
        writer.writerow(
            [
                v.recorded_at.isoformat(),
                v.systolic,
                v.diastolic,
                v.heart_rate,
                v.blood_glucose,
                v.glucose_context,
                v.weight_kg,
                v.notes or "",
            ]
        )
    return buf.getvalue()


def patient_pdf(user: User, vitals: list[VitalReading], medications: list[Medication]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _latin1(f"Health Report: {user.name}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 9)
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(0, 6, f"Generated {generated}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    # Summary of latest reading
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Latest reading", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if vitals:
        latest = vitals[0]
        assessment = assess_reading(
            systolic=latest.systolic,
            diastolic=latest.diastolic,
            heart_rate=latest.heart_rate,
            blood_glucose=latest.blood_glucose,
            glucose_context=latest.glucose_context,
            weight_kg=latest.weight_kg,
            height_cm=user.height_cm,
        )
        pdf.cell(0, 6, f"Overall status: {assessment.overall.upper()}", new_x="LMARGIN", new_y="NEXT")
        for f in assessment.findings:
            pdf.multi_cell(0, 6, _latin1(f"- {METRIC_LABELS[f.metric]}: {f.value} ({f.category})"), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "No readings logged yet.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # History table
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Recent readings", new_x="LMARGIN", new_y="NEXT")
    headers = ["Date", "BP (mmHg)", "HR (bpm)", "Glucose (mg/dL)", "Weight (kg)"]
    widths = [50, 32, 28, 40, 30]
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for v in vitals[:20]:
        row = [
            v.recorded_at.strftime("%Y-%m-%d %H:%M"),
            f"{v.systolic}/{v.diastolic}",
            str(v.heart_rate),
            f"{v.blood_glucose} ({v.glucose_context[0].upper()})",
            f"{v.weight_kg:g}",
        ]
        for value, w in zip(row, widths):
            pdf.cell(w, 7, value, border=1, align="C")
        pdf.ln()
    pdf.ln(3)

    # Medications
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Active medications", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    active = [m for m in medications if m.active]
    if not active:
        pdf.cell(0, 6, "None recorded.", new_x="LMARGIN", new_y="NEXT")
    for m in active:
        pdf.cell(0, 6, _latin1(f"- {m.name} {m.dosage} at {m.schedule_time} (stock: {m.stock})"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _latin1(DISCLAIMER))
    return bytes(pdf.output())
