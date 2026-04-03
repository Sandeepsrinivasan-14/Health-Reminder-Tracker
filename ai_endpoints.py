from ai_service import ai_service
from pydantic import BaseModel

class AIQuery(BaseModel):
    query: str
    health_data: dict = None

class HealthRiskRequest(BaseModel):
    health_data: dict

# Add to backend.py (after existing imports)

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

@app.get("/api/ai/status")
async def ai_status():
    \"\"\"Check AI service status\"\"\"
    return {
        'openai_available': ai_service.openai_key is not None,
        'gemini_available': ai_service.gemini_key is not None,
        'provider': ai_service.provider
    }
