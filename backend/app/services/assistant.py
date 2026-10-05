"""Health assistant: an optional LLM (Groq, OpenAI-compatible API) with a rule-based fallback.

The LLM is always grounded in the deterministic risk assessment and instructed to stay
educational: it explains readings and suggests questions for a doctor, but it does not
diagnose or recommend starting, stopping or changing medication.
"""

import logging

import httpx

from ..config import Settings
from ..risk import METRIC_LABELS
from ..schemas import Assessment

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a careful health-education assistant inside a personal health tracker.
You help a patient understand their own logged readings (blood pressure, heart rate, blood glucose, weight).

Rules:
- Ground every statement in the readings and the threshold assessment you are given. Do not invent values.
- Explain what the numbers mean in plain language and suggest practical lifestyle steps.
- You are not a doctor. Never diagnose, and never tell the patient to start, stop or change a medication or dose.
  Suggest questions they can ask their clinician instead.
- If any finding is marked "urgent", say clearly that they should seek medical care now (emergency number in India: 112).
- Keep answers under 200 words and use short paragraphs or bullet points."""

GENERIC_TIPS = [
    "Measure blood pressure at the same time each day, seated, after 5 minutes of rest.",
    "Aim for at least 150 minutes of moderate activity (e.g. brisk walking) per week.",
    "Keep added salt under 5 g a day; packaged and restaurant food is the main source.",
    "Take medicines at the same time daily; pair them with a routine like breakfast.",
    "Aim for 7 to 9 hours of sleep; poor sleep raises blood pressure and blood sugar.",
]


class HealthAssistant:
    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self.settings = settings
        self._client = client

    # ---------- public API ----------

    def answer(self, question: str, readings: list[dict], assessment: Assessment | None) -> tuple[str, str]:
        """Return (answer, source) where source is "llm" or "rules"."""
        if self.settings.llm_enabled:
            context = self._context(readings, assessment)
            try:
                return self._chat([{"role": "user", "content": f"{context}\n\nPatient question: {question}"}]), "llm"
            except Exception as exc:  # network, auth or quota problems: fall back gracefully
                logger.warning("LLM request failed, using rule-based answer: %s", exc)
        return self._rule_based_answer(question, assessment), "rules"

    def tips(self, readings: list[dict], assessment: Assessment | None) -> tuple[list[str], str]:
        if self.settings.llm_enabled and readings:
            context = self._context(readings, assessment)
            prompt = (
                f"{context}\n\nGive exactly 5 short, practical lifestyle tips tailored to these readings, "
                "one per line, no numbering, no medication advice."
            )
            try:
                text = self._chat([{"role": "user", "content": prompt}])
                tips = [line.strip(" -•*\t") for line in text.splitlines() if line.strip(" -•*\t")]
                if tips:
                    return tips[:5], "llm"
            except Exception as exc:
                logger.warning("LLM tips request failed, using rule-based tips: %s", exc)
        return self._rule_based_tips(assessment), "rules"

    # ---------- internals ----------

    def _chat(self, messages: list[dict]) -> str:
        payload = {
            "model": self.settings.groq_model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            "temperature": 0.3,
            "max_tokens": 600,
        }
        headers = {"Authorization": f"Bearer {self.settings.groq_api_key}"}
        client = self._client or httpx.Client(timeout=30)
        try:
            resp = client.post(f"{self.settings.groq_base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        finally:
            if self._client is None:
                client.close()

    @staticmethod
    def _context(readings: list[dict], assessment: Assessment | None) -> str:
        lines = ["Recent readings (newest first):"]
        if not readings:
            lines.append("- none logged yet")
        for r in readings[:5]:
            lines.append(
                f"- {r['recorded_at']}: BP {r['systolic']}/{r['diastolic']} mmHg, HR {r['heart_rate']} bpm, "
                f"glucose {r['blood_glucose']} mg/dL ({r['glucose_context']}), weight {r['weight_kg']} kg"
            )
        if assessment:
            lines.append(f"Threshold assessment of the latest reading (overall: {assessment.overall}):")
            for f in assessment.findings:
                lines.append(f"- {f.metric}: {f.value} -> {f.category} [{f.severity}]")
        return "\n".join(lines)

    @staticmethod
    def _rule_based_answer(question: str, assessment: Assessment | None) -> str:
        q = question.lower()
        topic_map = {
            "blood_pressure": ("pressure", "bp", "hypertension"),
            "blood_glucose": ("sugar", "glucose", "diabetes"),
            "heart_rate": ("heart", "pulse", "bpm"),
            "bmi": ("weight", "bmi"),
        }
        if assessment is None:
            return (
                "I don't have any readings for you yet. Log a reading on the dashboard and I can explain "
                "what your blood pressure, heart rate, glucose and weight numbers mean."
            )
        wanted = [m for m, keys in topic_map.items() if any(k in q for k in keys)]
        findings = [f for f in assessment.findings if not wanted or f.metric in wanted]
        parts = [f"**{METRIC_LABELS[f.metric]}**: {f.value} is in the *{f.category}* category. {f.advice}" for f in findings]
        if any(k in q for k in ("medicine", "medication", "tablet", "dose")):
            parts.append(
                "For questions about starting, stopping or changing a medicine, please ask your doctor or pharmacist; "
                "the medication page can help you track doses and stock."
            )
        if assessment.overall == "urgent":
            parts.insert(0, "⚠️ At least one reading is in an urgent range. If you feel unwell, seek medical care now (112).")
        return "\n\n".join(parts)

    @staticmethod
    def _rule_based_tips(assessment: Assessment | None) -> list[str]:
        if assessment is None:
            return GENERIC_TIPS
        tips = [f.advice for f in assessment.findings if f.severity != "normal"]
        for tip in GENERIC_TIPS:
            if len(tips) >= 5:
                break
            tips.append(tip)
        return tips[:5]
