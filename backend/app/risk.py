"""Deterministic, threshold-based assessment of a vitals reading.

Thresholds follow widely used adult reference ranges:
  * Blood pressure: 2017 ACC/AHA categories (normal, elevated, stage 1, stage 2, crisis).
  * Fasting glucose: ADA cut-offs (70-99 normal, 100-125 prediabetes range, >=126 diabetes range);
    random / post-meal glucose >= 200 mg/dL is treated as high. < 70 is low, < 54 is urgent.
  * Resting heart rate: 60-100 bpm; < 40 or > 130 bpm at rest is flagged urgent.
  * BMI (if height is known): WHO categories.

This is a screening aid for the patient and their caretaker, not a diagnosis.
"""

from .schemas import Assessment, Finding

DISCLAIMER = (
    "This assessment is informational only and is not a medical diagnosis. "
    "Discuss any abnormal readings with a qualified clinician. If you have chest pain, "
    "shortness of breath, confusion, fainting or weakness on one side, call emergency services (112 in India)."
)

METRIC_LABELS = {"blood_pressure": "Blood pressure", "heart_rate": "Heart rate", "blood_glucose": "Blood glucose", "bmi": "BMI"}

SEVERITY_ORDER = {"normal": 0, "watch": 1, "high": 2, "urgent": 3}


def assess_blood_pressure(systolic: int, diastolic: int) -> Finding:
    value = f"{systolic}/{diastolic} mmHg"
    if systolic > 180 or diastolic > 120:
        return Finding(
            metric="blood_pressure",
            value=value,
            category="Hypertensive crisis range",
            severity="urgent",
            advice="Re-measure after 5 minutes of rest. If it stays this high, or you have symptoms, seek emergency care now.",
        )
    if systolic >= 140 or diastolic >= 90:
        return Finding(
            metric="blood_pressure",
            value=value,
            category="Stage 2 hypertension range",
            severity="high",
            advice="Book a doctor's appointment soon to review this reading and your treatment plan.",
        )
    if systolic >= 130 or diastolic >= 80:
        return Finding(
            metric="blood_pressure",
            value=value,
            category="Stage 1 hypertension range",
            severity="watch",
            advice="Keep tracking. Reduce salt, stay active and mention the trend at your next check-up.",
        )
    if systolic >= 120:
        return Finding(
            metric="blood_pressure",
            value=value,
            category="Elevated",
            severity="watch",
            advice="Slightly above normal. Lifestyle measures (diet, exercise, sleep) usually help.",
        )
    if systolic < 90 or diastolic < 60:
        return Finding(
            metric="blood_pressure",
            value=value,
            category="Low blood pressure",
            severity="watch",
            advice="If you feel dizzy or faint, sit down, hydrate and contact your doctor.",
        )
    return Finding(metric="blood_pressure", value=value, category="Normal", severity="normal", advice="In the normal range.")


def assess_heart_rate(bpm: int) -> Finding:
    value = f"{bpm} bpm"
    if bpm < 40 or bpm > 130:
        return Finding(
            metric="heart_rate",
            value=value,
            category="Far outside resting range",
            severity="urgent",
            advice="If this is a resting reading, or you feel unwell, seek medical help promptly.",
        )
    if bpm > 100:
        return Finding(
            metric="heart_rate",
            value=value,
            category="Above resting range",
            severity="high",
            advice="Re-check after resting for 5 minutes. Persistent resting rates above 100 bpm need review.",
        )
    if bpm < 60:
        return Finding(
            metric="heart_rate",
            value=value,
            category="Below resting range",
            severity="watch",
            advice="Common in fit people. Report it if you feel dizzy, tired or short of breath.",
        )
    return Finding(metric="heart_rate", value=value, category="Normal", severity="normal", advice="In the normal resting range.")


def assess_glucose(mg_dl: int, context: str = "fasting") -> Finding:
    value = f"{mg_dl} mg/dL ({context.replace('_', '-')})"
    if mg_dl < 54:
        return Finding(
            metric="blood_glucose",
            value=value,
            category="Severe low",
            severity="urgent",
            advice="Take 15 g of fast-acting sugar now, re-check in 15 minutes and get help if it does not rise.",
        )
    if mg_dl < 70:
        return Finding(
            metric="blood_glucose",
            value=value,
            category="Low",
            severity="high",
            advice="Have a fast-acting carbohydrate and re-check in 15 minutes.",
        )
    if context == "fasting":
        if mg_dl >= 126:
            return Finding(
                metric="blood_glucose",
                value=value,
                category="Diabetes range (fasting)",
                severity="high",
                advice="Repeated fasting values at this level need a doctor's review (e.g. an HbA1c test).",
            )
        if mg_dl >= 100:
            return Finding(
                metric="blood_glucose",
                value=value,
                category="Prediabetes range (fasting)",
                severity="watch",
                advice="Worth discussing with your doctor; diet and activity changes are effective here.",
            )
        return Finding(
            metric="blood_glucose", value=value, category="Normal", severity="normal", advice="In the normal fasting range."
        )
    if mg_dl >= 300:
        return Finding(
            metric="blood_glucose",
            value=value,
            category="Very high",
            severity="urgent",
            advice="Very high glucose. Contact your doctor today; seek urgent care if you are vomiting or drowsy.",
        )
    if mg_dl >= 200:
        return Finding(
            metric="blood_glucose",
            value=value,
            category="High (non-fasting)",
            severity="high",
            advice="Non-fasting values of 200 mg/dL or more should be reviewed by a doctor.",
        )
    if mg_dl >= 140:
        return Finding(
            metric="blood_glucose",
            value=value,
            category="Above typical non-fasting",
            severity="watch",
            advice="Keep an eye on it and log a fasting reading for comparison.",
        )
    return Finding(metric="blood_glucose", value=value, category="Normal", severity="normal", advice="In the normal range.")


def compute_bmi(weight_kg: float, height_cm: float | None) -> float | None:
    if not height_cm:
        return None
    metres = height_cm / 100
    return round(weight_kg / (metres * metres), 1)


def assess_bmi(bmi: float) -> Finding:
    value = f"{bmi}"
    if bmi < 18.5:
        return Finding(
            metric="bmi",
            value=value,
            category="Underweight",
            severity="watch",
            advice="Talk to your doctor or a dietitian about healthy weight gain.",
        )
    if bmi < 25:
        return Finding(metric="bmi", value=value, category="Healthy weight", severity="normal", advice="In the healthy range.")
    if bmi < 30:
        return Finding(
            metric="bmi",
            value=value,
            category="Overweight",
            severity="watch",
            advice="Gradual changes to diet and activity can lower your BMI and blood pressure.",
        )
    return Finding(
        metric="bmi",
        value=value,
        category="Obesity",
        severity="high",
        advice="Ask your doctor about a structured weight-management plan.",
    )


def assess_reading(
    *,
    systolic: int,
    diastolic: int,
    heart_rate: int,
    blood_glucose: int,
    glucose_context: str,
    weight_kg: float,
    height_cm: float | None = None,
) -> Assessment:
    findings = [
        assess_blood_pressure(systolic, diastolic),
        assess_heart_rate(heart_rate),
        assess_glucose(blood_glucose, glucose_context),
    ]
    bmi = compute_bmi(weight_kg, height_cm)
    if bmi is not None:
        findings.append(assess_bmi(bmi))
    overall = max((f.severity for f in findings), key=SEVERITY_ORDER.__getitem__)
    return Assessment(overall=overall, findings=findings, bmi=bmi, disclaimer=DISCLAIMER)
