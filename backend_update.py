from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sqlite3
import os
from ai_service import ai_service

app = FastAPI(title="Health Reminder Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "health_tracker.db"

class AIQuery(BaseModel):
    query: str
    health_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = "default"

class HealthRiskRequest(BaseModel):
    health_data: Dict[str, Any]

@app.post("/api/ai/chat")
async def ai_chat(request: AIQuery):
    result = ai_service.get_health_advice(
        request.query, 
        request.health_data,
        request.session_id
    )
    return result

@app.post("/api/ai/health-risk")
async def predict_health_risk(request: HealthRiskRequest):
    result = ai_service.predict_health_risk(request.health_data)
    return result

@app.get("/api/ai/status")
async def ai_status():
    return {
        'gemini_available': ai_service.gemini_key is not None,
        'provider': ai_service.provider,
        'status': 'active' if ai_service.gemini_key else 'fallback'
    }

# ... rest of your backend code remains the same
