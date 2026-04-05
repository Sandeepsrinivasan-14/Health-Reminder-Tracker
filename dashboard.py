import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
import plotly.express as px

st.set_page_config(page_title="Medical Health Tracker", page_icon="🏥", layout="wide")

API_URL = "http://localhost:8000"

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
    .user-btn { padding: 10px; background: #f3f4f6; border: none; border-radius: 25px; cursor: pointer; font-size: 13px; text-align: center; }
    .user-btn:hover { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .user-btn-active { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .chat-container { height: 400px; overflow-y: auto; padding: 15px; background: #f9fafb; border-radius: 15px; margin-bottom: 15px; display: flex; flex-direction: column; }
    .user-message { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px 16px; border-radius: 18px; margin: 6px 0; max-width: 80%; align-self: flex-end; }
    .ai-message { background: white; color: #1f2937; padding: 10px 16px; border-radius: 18px; margin: 6px 0; max-width: 80%; align-self: flex-start; }
    .typing-indicator { background: #e5e7eb; color: #6b7280; padding: 10px 16px; border-radius: 18px; margin: 6px 0; max-width: 60%; align-self: flex-start; }
    .tip-item { padding: 12px; margin-bottom: 8px; background: rgba(16,185,129,0.08); border-radius: 10px; border-left: 4px solid #10b981; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🏥 Medical Health Tracker</h1><p>AI-Powered Healthcare Assistant</p><div style="margin-top:10px"><span style="background:#10b981; padding:6px 16px; border-radius:50px; color:white">✅ API: Healthy</span></div></div>', unsafe_allow_html=True)

# Load users
@st.cache_data(ttl=30)
def load_users():
    try:
        response = requests.get(f"{API_URL}/users", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=30)
def load_health_records(user_id):
    try:
        response = requests.get(f"{API_URL}/health-data/user/{user_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=60)
def load_health_tips():
    try:
        response = requests.get(f"{API_URL}/health-tips", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return ["Check blood pressure regularly", "Exercise 30 minutes daily", "Stay hydrated", "Get 7-8 hours of sleep", "Take medications on time"]

users = load_users()

# Session state
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'is_thinking' not in st.session_state:
    st.session_state.is_thinking = False
if 'risk_result' not in st.session_state:
    st.session_state.risk_result = None
if 'show_tips' not in st.session_state:
    st.session_state.show_tips = False
if 'health_records' not in st.session_state:
    st.session_state.health_records = []
if 'bp_sys' not in st.session_state:
    st.session_state.bp_sys = 120
if 'bp_dia' not in st.session_state:
    st.session_state.bp_dia = 80
if 'heart_rate' not in st.session_state:
    st.session_state.heart_rate = 72
if 'blood_sugar' not in st.session_state:
    st.session_state.blood_sugar = 110
if 'weight' not in st.session_state:
    st.session_state.weight = 70.0
if 'medicine_reminders' not in st.session_state:
    st.session_state.medicine_reminders = []

def send_ai_message(message, user_id):
    try:
        response = requests.post(f"{API_URL}/api/ai/chat", json={
            "query": message,
            "health_data": None,
            "session_id": str(user_id)
        }, timeout=30)
        if response.status_code == 200:
            return response.json().get('response', 'Sorry, no response')
    except:
        pass
    return "Sorry, I could not process that. Please try again."

def load_medicine_reminders(user_id):
    try:
        response = requests.get(f"{API_URL}/api/medicine-reminder/list/{user_id}", timeout=5)
        if response.status_code == 200:
            return response.json().get('reminders', [])
    except:
        pass
    return []

# Layout - 2 columns
col_left, col_right = st.columns([1, 1])

with col_left:
    # PATIENT SELECTION
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 👤 Select Patient")
        
        if users:
            st.markdown(f"*Total Patients: {len(users)}*")
            st.markdown('<div class="user-grid">', unsafe_allow_html=True)
            
            for user in users:
                is_active = st.session_state.selected_user and st.session_state.selected_user['id'] == user['id']
                if st.button(user['name'], key=f"user_{user['id']}", use_container_width=True):
                    st.session_state.selected_user = user
                    st.session_state.messages = []
                    st.session_state.health_records = load_health_records(user['id'])
                    st.session_state.medicine_reminders = load_medicine_reminders(user['id'])
                    
                    if st.session_state.health_records:
                        latest = st.session_state.health_records[0]
                        st.session_state.bp_sys = latest.get('bp_systolic', 120)
                        st.session_state.bp_dia = latest.get('bp_diastolic', 80)
                        st.session_state.heart_rate = latest.get('heart_rate', 72)
                        st.session_state.blood_sugar = latest.get('blood_sugar', 110)
                        st.session_state.weight = latest.get('weight', 70.0)
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.selected_user:
                st.markdown(f'<div style="background:rgba(16,185,129,0.1); padding:12px; border-radius:12px; margin-top:15px">✅ <strong>Selected: {st.session_state.selected_user["name"]}</strong></div>', unsafe_allow_html=True)
        else:
            st.error("⚠️ No users found. Make sure backend is running.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CREATE NEW PATIENT
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ Create New Patient")
        
        col_name, col_email = st.columns(2)
        with col_name:
            new_name = st.text_input("Name", key="new_name", placeholder="Full Name")
        with col_email:
            new_email = st.text_input("Email", key="new_email", placeholder="Email")
        
        if st.button("Create Patient", type="primary", use_container_width=True):
            if new_name and new_email:
                response = requests.post(f"{API_URL}/users", json={"name": new_name, "email": new_email})
                if response.status_code == 200:
                    st.success("✅ Patient created!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to create")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # HEALTH PARAMETERS
    if st.session_state.selected_user:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 📊 Health Parameters")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BP Systolic", f"{st.session_state.bp_sys} mmHg")
                bp_sys = st.number_input("", value=st.session_state.bp_sys, step=1, key="bp_sys_input", label_visibility="collapsed")
            with col2:
                st.metric("BP Diastolic", f"{st.session_state.bp_dia} mmHg")
                bp_dia = st.number_input("", value=st.session_state.bp_dia, step=1, key="bp_dia_input", label_visibility="collapsed")
            with col3:
                st.metric("Heart Rate", f"{st.session_state.heart_rate} BPM")
                heart_rate = st.number_input("", value=st.session_state.heart_rate, step=1, key="hr_input", label_visibility="collapsed")
            
            col4, col5 = st.columns(2)
            with col4:
                st.metric("Blood Sugar", f"{st.session_state.blood_sugar} mg/dL")
                blood_sugar = st.number_input("", value=st.session_state.blood_sugar, step=1, key="sugar_input", label_visibility="collapsed")
            with col5:
                st.metric("Weight", f"{st.session_state.weight} kg")
                weight = st.number_input("", value=st.session_state.weight, step=0.5, key="weight_input", label_visibility="collapsed")
            
            st.markdown("---")
            
            col_save, col_analyze = st.columns(2)
            with col_save:
                if st.button("💾 Save Health Data", use_container_width=True):
                    data = {
                        "user_id": st.session_state.selected_user["id"],
                        "bp_systolic": bp_sys,
                        "bp_diastolic": bp_dia,
                        "heart_rate": heart_rate,
                        "blood_sugar": blood_sugar,
                        "weight": weight
                    }
                    response = requests.post(f"{API_URL}/health-data", json=data)
                    if response.status_code == 200:
                        st.success("✅ Health data saved!")
                        st.session_state.health_records = load_health_records(st.session_state.selected_user["id"])
                        st.rerun()
            
            with col_analyze:
                if st.button("📊 Analyze Health Status", use_container_width=True):
                    risk_data = {
                        "health_data": {
                            "bp_systolic": bp_sys,
                            "bp_diastolic": bp_dia,
                            "heart_rate": heart_rate,
                            "blood_sugar": blood_sugar,
                            "weight": weight
                        }
                    }
                    response = requests.post(f"{API_URL}/api/ai/health-risk", json=risk_data)
                    if response.status_code == 200:
                        st.session_state.risk_result = response.json()
            
            if st.session_state.risk_result:
                risk = st.session_state.risk_result
                risk_class = "risk-high" if risk.get('risk_level') == 'HIGH' else "risk-low"
                st.markdown(f'<div class="{risk_class}"><strong>Risk Level: {risk.get("risk_level")}</strong><br><strong>Issues:</strong> {", ".join(risk.get("risks", [])) or "None"}<br><strong>Recommendations:</strong> {"; ".join(risk.get("recommendations", []))}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # SOS CARD
    with st.container():
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 🚨 Emergency SOS")
        
        if st.button("🚨 SOS EMERGENCY", use_container_width=True):
            try:
                response = requests.post(f"{API_URL}/sos")
                if response.status_code == 200:
                    st.success("✅ SOS Alert Sent!")
                else:
                    st.warning("⚠️ SOS would be sent here")
            except:
                st.warning("⚠️ SOS would be sent here")
        
        col_pdf, col_whatsapp = st.columns(2)
        with col_pdf:
            if st.button("📄 PDF Report", use_container_width=True):
                if st.session_state.selected_user:
                    pdf_url = f"{API_URL}/export-pdf/{st.session_state.selected_user['id']}"
                    st.markdown(f'<a href="{pdf_url}" target="_blank"><button style="width:100%; padding:10px; background:#ef4444; color:white; border:none; border-radius:10px">Download</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI CHAT
    if st.session_state.selected_user:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 🤖 AI Health Assistant")
            st.markdown(f"*Chatting with: {st.session_state.selected_user['name']}*")
            
            chat_html = '<div class="chat-container">'
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    chat_html += f'<div class="user-message">👤 {msg["content"]}</div>'
                else:
                    chat_html += f'<div class="ai-message">🤖 {msg["content"]}</div>'
            if st.session_state.is_thinking:
                chat_html += '<div class="typing-indicator">🤖 AI is thinking...</div>'
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
            
            col_input, col_send = st.columns([4, 1])
            with col_input:
                user_input = st.text_input("", key="chat_input", placeholder="Type your health question...", label_visibility="collapsed")
            with col_send:
                if st.button("Send", use_container_width=True):
                    if user_input:
                        st.session_state.messages.append({'role': 'user', 'content': user_input})
                        st.session_state.is_thinking = True
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get('is_thinking', False) and st.session_state.selected_user:
        response = send_ai_message(user_input, st.session_state.selected_user['id'])
        st.session_state.messages.append({'role': 'assistant', 'content': response})
        st.session_state.is_thinking = False
        st.rerun()
    
    # MEDICINE REMINDERS
    if st.session_state.selected_user:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 💊 Medicine Reminders")
            
            col_med1, col_med2 = st.columns(2)
            with col_med1:
                med_name = st.text_input("Medicine Name", key="med_name", placeholder="e.g., Metformin")
                med_dosage = st.text_input("Dosage", key="med_dosage", placeholder="e.g., 500mg")
            with col_med2:
                med_time = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"], key="med_time")
                med_reminder_time = st.time_input("Reminder Time", value=datetime.now().time(), key="med_time_input")
            
            if st.button("➕ Add Medicine Reminder", use_container_width=True):
                if med_name and med_dosage:
                    reminder_time_str = med_reminder_time.strftime("%H:%M")
                    try:
                        response = requests.post(f"{API_URL}/api/medicine-reminder/add", json={
                            "user_id": st.session_state.selected_user["id"],
                            "medicine_name": med_name,
                            "dosage": med_dosage,
                            "time_of_day": med_time,
                            "reminder_time": reminder_time_str
                        })
                        if response.status_code == 200:
                            st.success(f"✅ Reminder added for {med_name} at {reminder_time_str}")
                            st.session_state.medicine_reminders = load_medicine_reminders(st.session_state.selected_user["id"])
                            st.rerun()
                        else:
                            st.error("Failed to add reminder")
                    except:
                        st.error("Backend not running. Make sure backend is started.")
            
            # Show existing reminders
            if st.session_state.medicine_reminders:
                st.markdown("#### 📋 Active Reminders")
                for r in st.session_state.medicine_reminders:
                    st.markdown(f'<div class="tip-item">💊 <b>{r["medicine_name"]}</b> - {r["dosage"]} at {r["reminder_time"]} ({r["time_of_day"]})</div>', unsafe_allow_html=True)
            
            if st.button("🔔 Test Reminder Sound", use_container_width=True):
                try:
                    requests.post(f"{API_URL}/api/medicine-reminder/test/{st.session_state.selected_user['id']}")
                    st.success("Test notification sent! Check your screen.")
                except:
                    st.error("Backend not running")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # HEALTH TIPS
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💡 Health Tips")
        
        if st.button("📋 Load Health Tips", use_container_width=True):
            st.session_state.health_tips = load_health_tips()
            st.session_state.show_tips = True
        
        if st.session_state.get('show_tips', False):
            for tip in st.session_state.get('health_tips', []):
                st.markdown(f'<div class="tip-item">✓ {tip}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# HEALTH RECORDS TABLE (Full Width)
if st.session_state.selected_user:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 📋 Recent Health Records - {st.session_state.selected_user['name']}")
    
    records = load_health_records(st.session_state.selected_user['id'])
    
    if records:
        df = pd.DataFrame(records)
        df['recorded_at'] = pd.to_datetime(df['recorded_at']).dt.strftime('%Y-%m-%d %H:%M')
        df = df.rename(columns={
            'recorded_at': 'Date & Time',
            'bp_systolic': 'BP Sys',
            'bp_diastolic': 'BP Dia',
            'heart_rate': 'HR',
            'blood_sugar': 'Sugar',
            'weight': 'Weight (kg)'
        })
        st.dataframe(df[['Date & Time', 'BP Sys', 'BP Dia', 'HR', 'Sugar', 'Weight (kg)']], use_container_width=True, height=300)
    else:
        st.info("📭 No health records yet. Add your first health record above!")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center>🏥 Medical Health Tracker | AI-Powered Healthcare Assistant | Made with ❤️</center>", unsafe_allow_html=True)
