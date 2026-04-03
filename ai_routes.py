from ai_service import ai_service
from pydantic import BaseModel
from typing import List, Optional

class AIQuery(BaseModel):
    query: str
    health_data: dict = None

class HealthRiskRequest(BaseModel):
    health_data: dict

class TrendAnalysisRequest(BaseModel):
    health_history: List[dict]

class MedicationSuggestRequest(BaseModel):
    medications: List[dict]

# Add these routes to backend.py (after existing routes)

@app.post("/api/ai/chat")
async def ai_chat(request: AIQuery):
    \"\"\"AI Health Assistant Chat Endpoint\"\"\"
    result = ai_service.get_health_advice(request.query, request.health_data)
    return result

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: HealthRiskRequest):
    \"\"\"Predict health risks from health data\"\"\"
    result = ai_service.predict_health_risk(request.health_data)
    return result

@app.post("/api/ai/trend-analysis")
async def analyze_trends(request: TrendAnalysisRequest):
    \"\"\"Analyze health trends\"\"\"
    result = ai_service.analyze_health_trends(request.health_history)
    return result

@app.post("/api/ai/medication-suggest")
async def suggest_medications(request: MedicationSuggestRequest):
    \"\"\"Get medication reminder suggestions\"\"\"
    result = ai_service.suggest_medication_reminder(request.medications)
    return result

@app.get("/api/ai/status")
async def ai_status():
    \"\"\"Check AI service status\"\"\"
    return {
        'gemini_available': ai_service.gemini_key is not None and GEMINI_AVAILABLE,
        'provider': ai_service.provider,
        'status': 'active' if ai_service.gemini_key else 'fallback'
    }
