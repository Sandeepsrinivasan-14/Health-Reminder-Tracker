import streamlit as st
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="Medical Health Tracker", page_icon="🏥", layout="wide")

# HARDCODED USERS - Works without backend
USERS = [
    {"id": 1, "name": "Test Patient", "condition": "Healthy", "bp_sys": 118, "bp_dia": 78, "hr": 72, "sugar": 95, "weight": 68},
    {"id": 2, "name": "Rajesh Kumar", "condition": "Diabetes", "bp_sys": 135, "bp_dia": 85, "hr": 78, "sugar": 180, "weight": 75},
    {"id": 3, "name": "Priya Sharma", "condition": "Healthy", "bp_sys": 118, "bp_dia": 78, "hr": 72, "sugar": 95, "weight": 68},
    {"id": 4, "name": "Amit Patel", "condition": "Heart Disease", "bp_sys": 145, "bp_dia": 90, "hr": 95, "sugar": 115, "weight": 78},
    {"id": 5, "name": "Sunita Reddy", "condition": "Hypertension", "bp_sys": 155, "bp_dia": 95, "hr": 82, "sugar": 110, "weight": 80},
    {"id": 6, "name": "Vikram Singh", "condition": "Diabetes", "bp_sys": 135, "bp_dia": 85, "hr": 78, "sugar": 180, "weight": 75},
    {"id": 7, "name": "Neha Gupta", "condition": "Asthma", "bp_sys": 120, "bp_dia": 78, "hr": 75, "sugar": 95, "weight": 65},
    {"id": 8, "name": "Anand Desai", "condition": "Hypertension", "bp_sys": 155, "bp_dia": 95, "hr": 82, "sugar": 110, "weight": 80},
    {"id": 9, "name": "Kavita Nair", "condition": "Thyroid", "bp_sys": 125, "bp_dia": 80, "hr": 70, "sugar": 100, "weight": 85},
    {"id": 10, "name": "Suresh Iyer", "condition": "Heart Disease", "bp_sys": 145, "bp_dia": 90, "hr": 95, "sugar": 115, "weight": 78},
    {"id": 11, "name": "Meera Joshi", "condition": "Migraine", "bp_sys": 118, "bp_dia": 75, "hr": 68, "sugar": 92, "weight": 62},
    {"id": 12, "name": "Rohan Mehta", "condition": "Healthy", "bp_sys": 118, "bp_dia": 78, "hr": 72, "sugar": 95, "weight": 68},
    {"id": 13, "name": "Anjali Kulkarni", "condition": "Diabetes", "bp_sys": 135, "bp_dia": 85, "hr": 78, "sugar": 180, "weight": 75},
    {"id": 14, "name": "Deepak Saxena", "condition": "Obesity", "bp_sys": 140, "bp_dia": 88, "hr": 85, "sugar": 125, "weight": 110},
    {"id": 15, "name": "Swati Choudhary", "condition": "Anemia", "bp_sys": 105, "bp_dia": 65, "hr": 88, "sugar": 85, "weight": 55},
    {"id": 16, "name": "Manoj Verma", "condition": "Hypertension", "bp_sys": 155, "bp_dia": 95, "hr": 82, "sugar": 110, "weight": 80},
    {"id": 17, "name": "Pooja Malhotra", "condition": "Osteoporosis", "bp_sys": 130, "bp_dia": 82, "hr": 72, "sugar": 100, "weight": 60},
    {"id": 18, "name": "Arjun Nair", "condition": "Healthy", "bp_sys": 118, "bp_dia": 78, "hr": 72, "sugar": 95, "weight": 68},
    {"id": 19, "name": "Divya Menon", "condition": "PCOS", "bp_sys": 128, "bp_dia": 82, "hr": 76, "sugar": 115, "weight": 82},
    {"id": 20, "name": "Sanjay Gupta", "condition": "Diabetes", "bp_sys": 135, "bp_dia": 85, "hr": 78, "sugar": 180, "weight": 75},
    {"id": 21, "name": "Lata Mangeshkar", "condition": "Hypertension", "bp_sys": 155, "bp_dia": 95, "hr": 82, "sugar": 110, "weight": 80},
    {"id": 22, "name": "Lohith", "condition": "Healthy", "bp_sys": 118, "bp_dia": 78, "hr": 72, "sugar": 95, "weight": 68},
]

# Tips for conditions
TIPS = {
    "Diabetes": ["🩸 Monitor blood sugar daily", "🥗 Eat low glycemic index foods", "🚶 Walk after meals"],
    "Hypertension": ["❤️ Reduce salt intake", "🚶 Walk 30 mins daily", "💧 Drink more water"],
    "Heart Disease": ["💔 Take medications on time", "🚶 Light exercise only", "🥗 Low fat diet"],
    "Healthy": ["✅ Keep up the good work!", "🥗 Eat balanced diet", "🚶 Stay active"],
    "Asthma": ["🌬️ Use inhaler as prescribed", "🚶 Avoid triggers", "💨 Practice breathing"],
    "Thyroid": ["🦋 Take thyroid medication daily", "🥗 Eat iodine-rich foods", "🩸 Regular checkups"],
    "Obesity": ["⚖️ Track calories", "🚶 Walk 10k steps", "🥗 Eat more protein"],
    "Anemia": ["🩸 Eat iron-rich foods", "🥬 Eat spinach", "💊 Take iron supplements"],
    "PCOS": ["🌸 Maintain healthy weight", "🥗 Low carb diet", "🚶 Regular exercise"],
    "Migraine": ["🧠 Avoid triggers", "💧 Stay hydrated", "😴 Regular sleep"],
    "Osteoporosis": ["🦴 Increase calcium", "☀️ Get Vitamin D", "🏋️ Weight bearing exercises"]
}

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; margin-bottom: 20px; }
    .card { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; margin-bottom: 20px; }
    .user-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-height: 350px; overflow-y: auto; padding: 5px; }
    .user-btn { padding: 10px; background: #f3f4f6; border: none; border-radius: 25px; cursor: pointer; font-size: 13px; text-align: center; }
    .user-btn:hover { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .user-btn-active { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .chat-container { height: 350px; overflow-y: auto; padding: 15px; background: #f9fafb; border-radius: 15px; margin-bottom: 15px; }
    .user-message { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px 16px; border-radius: 18px; margin: 6px 0; max-width: 80%; float: right; }
    .ai-message { background: white; color: #1f2937; padding: 10px 16px; border-radius: 18px; margin: 6px 0; max-width: 80%; float: left; }
    .risk-high { background: #fee2e2; color: #dc2626; padding: 15px; border-radius: 12px; border-left: 4px solid #dc2626; }
    .risk-low { background: #d1fae5; color: #059669; padding: 15px; border-radius: 12px; border-left: 4px solid #059669; }
    .tip-item { padding: 12px; margin-bottom: 8px; background: rgba(16,185,129,0.08); border-radius: 10px; border-left: 4px solid #10b981; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🏥 Medical Health Tracker</h1><p>AI-Powered Healthcare Assistant</p><div style="margin-top:10px"><span style="background:#10b981; padding:6px 16px; border-radius:50px; color:white">✅ Standalone Mode</span></div></div>', unsafe_allow_html=True)

if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'risk_result' not in st.session_state:
    st.session_state.risk_result = None
if 'show_tips' not in st.session_state:
    st.session_state.show_tips = False

col_left, col_right = st.columns([1, 1])

with col_left:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 👤 Select Patient")
        st.markdown(f"*Total Patients: {len(USERS)}*")
        st.markdown('<div class="user-grid">', unsafe_allow_html=True)
        
        for user in USERS:
            is_active = st.session_state.selected_user and st.session_state.selected_user['id'] == user['id']
            if st.button(user['name'], key=f"user_{user['id']}", use_container_width=True):
                st.session_state.selected_user = user
                st.session_state.messages = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.selected_user:
            st.markdown(f'<div style="background:rgba(16,185,129,0.1); padding:12px; border-radius:12px; margin-top:15px">✅ <strong>Selected: {st.session_state.selected_user["name"]}</strong> - {st.session_state.selected_user["condition"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_user:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 📊 Health Parameters")
            
            user = st.session_state.selected_user
            
            bp_sys = st.number_input("BP Systolic", value=user["bp_sys"], step=1)
            bp_dia = st.number_input("BP Diastolic", value=user["bp_dia"], step=1)
            heart_rate = st.number_input("Heart Rate", value=user["hr"], step=1)
            blood_sugar = st.number_input("Blood Sugar", value=user["sugar"], step=1)
            weight = st.number_input("Weight (kg)", value=user["weight"], step=0.5)
            
            col_save, col_analyze = st.columns(2)
            with col_save:
                if st.button("💾 Save Health Data", use_container_width=True):
                    st.success("✅ Health data saved!")
            with col_analyze:
                if st.button("📊 Analyze Health Status", use_container_width=True):
                    risks = []
                    if bp_sys > 140 or bp_dia > 90:
                        risks.append("High Blood Pressure")
                    if heart_rate > 100:
                        risks.append("High Heart Rate")
                    if blood_sugar > 140:
                        risks.append("High Blood Sugar")
                    level = "HIGH" if len(risks) > 1 else "LOW"
                    st.session_state.risk_result = {"risk_level": level, "risks": risks}
            
            if st.session_state.risk_result:
                risk = st.session_state.risk_result
                risk_class = "risk-high" if risk.get('risk_level') == 'HIGH' else "risk-low"
                st.markdown(f'<div class="{risk_class}"><strong>Risk Level: {risk.get("risk_level")}</strong><br><strong>Issues:</strong> {", ".join(risk.get("risks", [])) or "None"}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    with st.container():
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 🚨 Emergency SOS")
        if st.button("🚨 SOS EMERGENCY", use_container_width=True):
            st.success("✅ SOS Alert Sent! Caregiver would be notified.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_user:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 🤖 AI Health Assistant")
            
            chat_html = '<div class="chat-container" style="height:300px; overflow-y:auto">'
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    chat_html += f'<div class="user-message">👤 {msg["content"]}</div>'
                else:
                    chat_html += f'<div class="ai-message">🤖 {msg["content"]}</div>'
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
            
            col_input, col_send = st.columns([4, 1])
            with col_input:
                user_input = st.text_input("", key="chat_input", placeholder="Ask about health...", label_visibility="collapsed")
            with col_send:
                if st.button("Send", use_container_width=True):
                    if user_input:
                        st.session_state.messages.append({'role': 'user', 'content': user_input})
                        condition = st.session_state.selected_user['condition']
                        if 'bp' in user_input.lower():
                            response = f"Normal BP is 120/80 mmHg. Your patient has {condition}. Maintain with exercise and low salt."
                        else:
                            response = f"I can help with health questions. {condition} patient needs regular monitoring."
                        st.session_state.messages.append({'role': 'assistant', 'content': response})
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💡 Health Tips")
        
        if st.button("📋 Load Health Tips", use_container_width=True):
            st.session_state.show_tips = True
        
        if st.session_state.get('show_tips', False) and st.session_state.selected_user:
            condition = st.session_state.selected_user['condition']
            tips = TIPS.get(condition, TIPS["Healthy"])
            for tip in tips:
                st.markdown(f'<div class="tip-item">✓ {tip}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.selected_user:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 📋 Health Summary - {st.session_state.selected_user['name']}")
    
    user = st.session_state.selected_user
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("BP Systolic", f"{user['bp_sys']} mmHg")
    with col2:
        st.metric("BP Diastolic", f"{user['bp_dia']} mmHg")
    with col3:
        st.metric("Heart Rate", f"{user['hr']} BPM")
    with col4:
        st.metric("Blood Sugar", f"{user['sugar']} mg/dL")
    with col5:
        st.metric("Weight", f"{user['weight']} kg")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center>🏥 Medical Health Tracker | AI-Powered Healthcare Assistant | Made with ❤️</center>", unsafe_allow_html=True)
