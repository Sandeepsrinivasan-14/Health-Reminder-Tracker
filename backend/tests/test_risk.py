import pytest

from app.risk import assess_blood_pressure, assess_glucose, assess_heart_rate, assess_reading, compute_bmi


@pytest.mark.parametrize(
    ("sys", "dia", "category", "severity"),
    [
        (115, 75, "Normal", "normal"),
        (125, 78, "Elevated", "watch"),
        (132, 78, "Stage 1 hypertension range", "watch"),
        (118, 84, "Stage 1 hypertension range", "watch"),
        (142, 85, "Stage 2 hypertension range", "high"),
        (128, 92, "Stage 2 hypertension range", "high"),
        (185, 100, "Hypertensive crisis range", "urgent"),
        (150, 125, "Hypertensive crisis range", "urgent"),
        (85, 55, "Low blood pressure", "watch"),
    ],
)
def test_blood_pressure_categories(sys, dia, category, severity):
    finding = assess_blood_pressure(sys, dia)
    assert finding.category == category
    assert finding.severity == severity


@pytest.mark.parametrize(("bpm", "severity"), [(72, "normal"), (55, "watch"), (110, "high"), (35, "urgent"), (140, "urgent")])
def test_heart_rate(bpm, severity):
    assert assess_heart_rate(bpm).severity == severity


@pytest.mark.parametrize(
    ("value", "context", "severity"),
    [
        (90, "fasting", "normal"),
        (110, "fasting", "watch"),
        (130, "fasting", "high"),
        (65, "fasting", "high"),
        (50, "random", "urgent"),
        (150, "random", "watch"),
        (210, "post_meal", "high"),
        (320, "random", "urgent"),
        (130, "random", "normal"),
    ],
)
def test_glucose(value, context, severity):
    assert assess_glucose(value, context).severity == severity


def test_bmi():
    assert compute_bmi(70, 175) == 22.9
    assert compute_bmi(70, None) is None


def test_overall_is_worst_finding():
    result = assess_reading(
        systolic=190, diastolic=95, heart_rate=72, blood_glucose=90, glucose_context="fasting", weight_kg=70, height_cm=175
    )
    assert result.overall == "urgent"
    assert {f.metric for f in result.findings} == {"blood_pressure", "heart_rate", "blood_glucose", "bmi"}
    assert "not a medical diagnosis" in result.disclaimer
