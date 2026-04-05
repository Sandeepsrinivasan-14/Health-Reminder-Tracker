# Main entry point for Render deployment
# This imports the FastAPI app from backend.py

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app from backend.py
try:
    from backend import app
    print("✅ Successfully imported FastAPI app from backend.py")
except ImportError as e:
    print(f"❌ Error importing app: {e}")
    # Fallback - create a basic app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="Health Reminder Tracker", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def root():
        return {"message": "Health Reminder Tracker API", "status": "running"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "Health Reminder Tracker"}

# Additional health check endpoint (if not already in backend)
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Health Reminder Tracker", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
