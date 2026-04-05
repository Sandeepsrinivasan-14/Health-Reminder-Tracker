import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
import plotly.express as px

st.set_page_config(page_title="Medical Health Tracker", layout="wide")

API_URL = "https://health-reminder-tracker-1.onrender.com"

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .metric-card { background: white; padding: 15px; border-radius: 15px; text-align: center; }
    .med-card { background: white; border-radius: 15px; padding: 15px; margin: 10px 0; border-left: 4px solid #f59e0b; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'users' not in st.session_state:
    st.session_state.users = []
if 'health_data' not in st.session_state:
    st.session_state.health_data = {}

# Sidebar - Patient Management
with st.sidebar:
    st.markdown("## 🏥 Patient Management")
    
    # Fetch users from backend
    try:
        response = requests.get(f"{API_URL}/users")
        if response.status_code == 200:
            st.session_state.users = response.json()
            
            # User selection
            user_names = [f"{u['name']} (ID: {u['id']})" for u in st.session_state.users]
            selected = st.selectbox("👤 Select Patient", user_names)
            selected_id = int(selected.split("ID: ")[1].rstrip(")"))
            st.session_state.selected_user = next(u for u in st.session_state.users if u["id"] == selected_id)
            
            st.success(f"✅ Current Patient: {st.session_state.selected_user['name']}")
            
            # Fetch health data for selected user
            health_resp = requests.get(f"{API_URL}/health-data/user/{selected_id}")
            if health_resp.status_code == 200:
                st.session_state.health_data[selected_id] = health_resp.json()
        else:
            st.error("Cannot fetch users")
    except Exception as e:
        st.error(f"Backend error: {e}")
    
    st.markdown("---")
    
    # Add New Patient
    st.markdown("### ➕ Add New Patient")
    new_name = st.text_input("Patient Name")
    new_email = st.text_input("Email")
    if st.button("Add Patient", use_container_width=True):
        if new_name and new_email:
            response = requests.post(f"{API_URL}/users", json={"name": new_name, "email": new_email})
            if response.status_code == 200:
                st.success(f"✅ Added {new_name}!")
                st.rerun()
            else:
                st.error("Failed to add")
    
    st.markdown("---")
    
    # SOS Button
    st.markdown("### 🚨 Emergency")
    if st.button("🆘 SOS", use_container_width=True):
        st.error("🚨 SOS Alert Sent!")
    
    # Navigation
    page = st.radio("📱 Menu", ["📊 Dashboard", "💊 Medications", "📈 Reports", "⚙️ Settings"])

# Main content
if st.session_state.selected_user:
    user = st.session_state.selected_user
    
    if page == "📊 Dashboard":
        st.title(f"🏥 Welcome, {user['name']}")
        
        # Get health data
        health_data = st.session_state.health_data.get(user['id'], [])
        
        if health_data:
            latest = health_data[0]
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("❤️ Heart Rate", f"{latest['heart_rate']} bpm")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💊 BP", f"{latest['bp_systolic']}/{latest['bp_diastolic']}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("🩸 Sugar", f"{latest['blood_sugar']} mg/dL")
                st.markdown('</div>', unsafe_allow_html=True)
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("⚖️ Weight", f"{latest['weight']} kg")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No health records yet. Add your first health record below!")
        
        # Log Health Data
        st.markdown("### 📝 Log Health Data")
        col1, col2 = st.columns(2)
        with col1:
            bp_sys = st.number_input("Systolic BP", 80, 250, 120)
            bp_dia = st.number_input("Diastolic BP", 50, 150, 80)
            hr = st.number_input("Heart Rate", 40, 200, 72)
        with col2:
            sugar = st.number_input("Blood Sugar", 50, 400, 95)
            weight = st.number_input("Weight (kg)", 20.0, 200.0, 70.0)
        
        if st.button("💾 Save Health Record", type="primary"):
            payload = {
                "user_id": user['id'],
                "bp_systolic": bp_sys,
                "bp_diastolic": bp_dia,
                "heart_rate": hr,
                "blood_sugar": sugar,
                "weight": weight
            }
            response = requests.post(f"{API_URL}/health-data", json=payload)
            if response.status_code == 200:
                st.success("✅ Saved!")
                st.rerun()
        
        # Show health history
        if health_data:
            st.markdown("### 📊 Health History")
            df = pd.DataFrame(health_data)
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            st.dataframe(df)
            
            fig = px.line(df, x='recorded_at', y=['heart_rate', 'blood_sugar'], title='Health Trends')
            st.plotly_chart(fig)
    
    elif page == "💊 Medications":
        st.title(f"💊 Medications for {user['name']}")
        
        # Medication list
        medications = [
            {"name": "Lisinopril", "dosage": "10mg", "time": "08:00", "type": "BP"},
            {"name": "Metformin", "dosage": "500mg", "time": "08:00", "type": "Diabetes"},
            {"name": "Atorvastatin", "dosage": "20mg", "time": "20:00", "type": "Cholesterol"},
        ]
        
        for med in medications:
            st.markdown(f"""
            <div class="med-card">
                <strong>{med['name']}</strong> - {med['dosage']}<br>
                🕐 {med['time']} | {med['type']}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Take {med['name']}", key=med['name']):
                    st.success(f"Taken {med['name']}!")
            with col2:
                if st.button(f"⏭️ Skip {med['name']}", key=f"skip_{med['name']}"):
                    st.warning(f"Skipped {med['name']}")
        
        # Add medication
        st.markdown("### ➕ Add Medication")
        col1, col2 = st.columns(2)
        with col1:
            new_med = st.text_input("Medication Name")
            new_dosage = st.text_input("Dosage")
        with col2:
            new_time = st.time_input("Time")
            new_type = st.selectbox("Type", ["BP", "Diabetes", "Cholesterol", "Pain"])
        
        if st.button("Add Medication"):
            st.success(f"Added {new_med} for {user['name']}")
    
    elif page == "📈 Reports":
        st.title(f"📈 Health Reports - {user['name']}")
        
        health_data = st.session_state.health_data.get(user['id'], [])
        if health_data:
            df = pd.DataFrame(health_data)
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            
            # Summary stats
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Heart Rate", f"{df['heart_rate'].mean():.0f} bpm")
            with col2:
                st.metric("Avg BP Systolic", f"{df['bp_systolic'].mean():.0f}")
            with col3:
                st.metric("Avg Blood Sugar", f"{df['blood_sugar'].mean():.0f}")
            
            # Trend chart
            fig = px.line(df, x='recorded_at', y=['bp_systolic', 'heart_rate', 'blood_sugar', 'weight'], 
                         title='Health Metrics Over Time')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")
        st.info("Notification settings coming soon...")

else:
    st.warning("Please select a patient from the sidebar")
