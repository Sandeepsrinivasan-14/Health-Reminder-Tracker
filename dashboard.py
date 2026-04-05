import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime, time
import plotly.express as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API URL from environment or use default
API_URL = os.getenv("API_URL", "http://localhost:8000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(page_title="Medical Health Tracker", page_icon="🏥", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; margin-bottom: 20px; }
    .card { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; margin-bottom: 20px; }
    .metric-card { background: white; padding: 15px; border-radius: 15px; text-align: center; }
    .risk-high { background: #fee2e2; color: #dc2626; padding: 15px; border-radius: 12px; border-left: 4px solid #dc2626; }
    .risk-low { background: #d1fae5; color: #059669; padding: 15px; border-radius: 12px; border-left: 4px solid #059669; }
    .user-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-height: 350px; overflow-y: auto; padding: 5px; }
</style>
""", unsafe_allow_html=True)

# Rest of your dashboard code continues here...
# (The rest of your existing dashboard.py content after line 20)
