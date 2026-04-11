import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
import plotly.express as px
import streamlit.components.v1 as components
import json
import base64
from fpdf import FPDF

st.set_page_config(page_title="Medical Health Tracker", layout="wide")

API_URL = "http://127.0.0.1:8000"

def create_pdf(df, name, meds):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Medical Health Report: {name}", ln=True, align='C')
    
    # Meta Info
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
    pdf.ln(5)
    
    # Summary Metrics
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Health Metrics Summary", ln=True)
    pdf.set_font("Arial", '', 11)
    
    avg_hr = df['heart_rate'].mean() if 'heart_rate' in df else 0
    avg_bps = df['bp_systolic'].mean() if 'bp_systolic' in df else 0
    avg_bpd = df['bp_diastolic'].mean() if 'bp_diastolic' in df else 0
    avg_sugar = df['blood_sugar'].mean() if 'blood_sugar' in df else 0
    
    pdf.cell(0, 8, f"Average Heart Rate: {avg_hr:.0f} bpm    |    Average BP: {avg_bps:.0f}/{avg_bpd:.0f}", ln=True)
    pdf.cell(0, 8, f"Average Blood Sugar: {avg_sugar:.0f} mg/dL", ln=True)
    pdf.ln(5)
    
    # Table Header for Historical Data
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Recent Health Records", ln=True)
    
    # Table Layout
    pdf.set_font("Arial", 'B', 10)
    col_widths = [45, 30, 30, 30, 30]
    headers = ["Date", "BP (Sys/Dia)", "Heart Rate", "Blood", "Weight"]
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 10, headers[i], border=1, align='C')
    pdf.ln(10)
    
    # Table Rows
    pdf.set_font("Arial", '', 10)
    for _, row in df.head(15).iterrows():
        date_str = str(row['recorded_at']).split('.')[0] if 'recorded_at' in row else ""
        pdf.cell(col_widths[0], 10, date_str, border=1, align='C')
        pdf.cell(col_widths[1], 10, f"{row.get('bp_systolic', '')}/{row.get('bp_diastolic', '')}", border=1, align='C')
        pdf.cell(col_widths[2], 10, f"{row.get('heart_rate', '')} bpm", border=1, align='C')
        pdf.cell(col_widths[3], 10, f"{row.get('blood_sugar', '')}", border=1, align='C')
        pdf.cell(col_widths[4], 10, f"{row.get('weight', '')} kg", border=1, align='C')
        pdf.ln(10)
        
    pdf.ln(5)
    
    # Medications
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Active Medications", ln=True)
    pdf.set_font("Arial", '', 11)
    
    for med in meds:
        pdf.cell(0, 8, f"- {med.get('name', 'N/A')}: {med.get('dosage', 'N/A')} at {med.get('time', 'N/A')}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); transition: filter 0.3s; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .med-card { background: white; border-radius: 15px; padding: 15px; margin: 10px 0; border-left: 4px solid #f59e0b; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .chat-user { background: #667eea; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right; }
    .chat-ai { background: #e5e7eb; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .stButton > button { width: 100%; }
    
    @keyframes blink {
        0% { filter: hue-rotate(0deg) contrast(100%); }
        50% { filter: hue-rotate(180deg) invert(20%) saturate(200%); }
        100% { filter: hue-rotate(0deg) contrast(100%); }
    }
    .blink-active { animation: blink 1s infinite !important; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'medications' not in st.session_state:
    st.session_state.medications = [
        {"name": "Lisinopril", "dosage": "10mg", "time": "08:00", "status": "pending", "type": "BP", "stock": 4},
        {"name": "Metformin", "dosage": "500mg", "time": "08:00", "status": "pending", "type": "Diabetes", "stock": 10},
        {"name": "Atorvastatin", "dosage": "20mg", "time": "20:00", "status": "pending", "type": "Cholesterol", "stock": 30},

    ]

# Client-Side Medication Alarm System — works locally AND on Render (same-origin iframe)
try:
    pending_meds = [m for m in st.session_state.medications if m['status'] == 'pending']
    meds_json = json.dumps(pending_meds)
    components.html(f"""
    <script>
    (function() {{
        const pendingMeds = {meds_json};
        let snoozed = {{}};
        let dismissed = new Set();
        let alarmInterval = null;
        let currentMed = null;

        // ── Inject modal + styles into PARENT page (same-origin on Render) ──
        function injectModal() {{
            const p = window.parent.document;
            if (p.getElementById('medReminderModal')) return;

            // Styles
            const style = p.createElement('style');
            style.textContent = `
                #medReminderModal {{
                    display:none; position:fixed; top:0; left:0; width:100%; height:100%;
                    background:rgba(0,0,0,0.88); z-index:999999;
                    justify-content:center; align-items:center;
                }}
                #medReminderBox {{
                    background:#fff; border-radius:20px; padding:40px 36px;
                    max-width:440px; width:92%; text-align:center;
                    animation: medPulse 1.2s ease-in-out infinite;
                }}
                @keyframes medPulse {{
                    0%,100% {{ box-shadow: 0 0 30px rgba(220,38,38,0.45); }}
                    50%  {{ box-shadow: 0 0 80px rgba(220,38,38,0.95); }}
                }}
                #medReminderBox h2 {{ color:#dc2626; font-size:26px; margin:12px 0 6px; }}
                #medReminderBox p  {{ font-size:17px; color:#374151; margin:6px 0; }}
                #medReminderBox .med-btn {{
                    border:none; padding:14px 28px; border-radius:12px;
                    font-size:17px; font-weight:700; cursor:pointer; margin:8px 6px 0;
                }}
                .med-taken  {{ background:#16a34a; color:#fff; }}
                .med-snooze {{ background:#f59e0b; color:#fff; }}
            `;
            p.head.appendChild(style);

            // HTML
            const div = p.createElement('div');
            div.id = 'medReminderModal';
            div.innerHTML = `
                <div id="medReminderBox">
                    <div style="font-size:58px">💊</div>
                    <h2 id="medReminderTitle">Medicine Time!</h2>
                    <p id="medReminderDetails"></p>
                    <p id="medReminderTime" style="font-size:13px;color:#9ca3af"></p>
                    <div>
                        <button class="med-btn med-taken"  onclick="window._medDismiss()">✅ Taken</button>
                        <button class="med-btn med-snooze" onclick="window._medSnooze()">⏰ Snooze 5 min</button>
                    </div>
                </div>
            `;
            p.body.appendChild(div);
        }}

        // ── Audio beep via Web Audio API (no files needed, works on Render) ──
        function playBeep() {{
            try {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                [[880,0,0.25],[660,0.3,0.25],[880,0.6,0.4]].forEach(([f,s,d]) => {{
                    const o = ctx.createOscillator(), g = ctx.createGain();
                    o.connect(g); g.connect(ctx.destination);
                    o.frequency.value = f; o.type = 'sine';
                    g.gain.setValueAtTime(0.4, ctx.currentTime+s);
                    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime+s+d);
                    o.start(ctx.currentTime+s); o.stop(ctx.currentTime+s+d);
                }});
            }} catch(e) {{}}
        }}

        // ── TTS (browser-native, works on Render) ──
        function speak(name, dosage) {{
            if (!window.parent.speechSynthesis) return;
            window.parent.speechSynthesis.cancel();
            const u = new window.parent.SpeechSynthesisUtterance(
                'Medication Alert! It is time to take your ' + name + ' ' + dosage + '. Please take your medicine now.'
            );
            u.rate = 0.88; u.pitch = 1.1; u.volume = 1;
            window.parent.speechSynthesis.speak(u);
        }}

        function showAlarm(med) {{
            currentMed = med;
            injectModal();
            const p = window.parent.document;
            p.getElementById('medReminderTitle').innerText   = '⏰ Time for ' + med.name;
            p.getElementById('medReminderDetails').innerText = med.dosage + ' — ' + (med.type || 'Medication');
            p.getElementById('medReminderTime').innerText    = 'Scheduled at ' + med.time;
            p.getElementById('medReminderModal').style.display = 'flex';

            // Red blink on body
            let blinks = 0;
            const bi = setInterval(() => {{
                p.body.style.transition = 'background 0.4s';
                p.body.style.background = blinks % 2 === 0 ? '#dc2626' : '';
                if (++blinks > 12) clearInterval(bi);
            }}, 500);

            alarmInterval = setInterval(playBeep, 3500);
            playBeep();
            speak(med.name, med.dosage);

            // Browser desktop notification (HTTPS on Render satisfies the requirement)
            if (window.parent.Notification && window.parent.Notification.permission === 'granted') {{
                new window.parent.Notification('💊 ' + med.name + ' reminder', {{
                    body: 'Take ' + med.dosage + ' now (scheduled ' + med.time + ')'
                }});
            }}
        }}

        window.parent._medDismiss = function() {{
            if (currentMed) {{
                dismissed.add(currentMed.name);
                try {{
                    const stored = JSON.parse(localStorage.getItem('medDismissed') || '[]');
                    stored.push(currentMed.name);
                    localStorage.setItem('medDismissed', JSON.stringify(stored));
                }} catch(e) {{}}
            }}
            window.parent.document.getElementById('medReminderModal').style.display = 'none';
            clearInterval(alarmInterval);
            if (window.parent.speechSynthesis) window.parent.speechSynthesis.cancel();
        }};
        window.parent._medSnooze = function() {{
            if (currentMed) snoozed[currentMed.name] = Date.now() + 5*60*1000;
            window.parent.document.getElementById('medReminderModal').style.display = 'none';
            clearInterval(alarmInterval);
            if (window.parent.speechSynthesis) window.parent.speechSynthesis.cancel();
        }};

        // Request desktop notification permission
        if (window.parent.Notification && window.parent.Notification.permission === 'default') {{
            window.parent.Notification.requestPermission();
        }}

        // ── Main check loop: every 30 s, fires within ±5 min of scheduled time ──
        function checkMedTimes() {{
            const now = new Date();
            const cur = now.getHours()*60 + now.getMinutes();
            // Reload dismissed from localStorage so rerenders don't re-trigger
            try {{
                const stored = JSON.parse(localStorage.getItem('medDismissed') || '[]');
                stored.forEach(n => dismissed.add(n));
            }} catch(e) {{}}

            pendingMeds.forEach(med => {{
                if (dismissed.has(med.name)) return;
                if (snoozed[med.name] && Date.now() < snoozed[med.name]) return;
                const [h,m] = med.time.split(':').map(Number);
                if (Math.abs(cur - (h*60+m)) <= 5) showAlarm(med);
            }});
        }}

        // Expose trigger so demo button can ring alarm immediately
        window.parent._triggerMedAlarm = showAlarm;

        checkMedTimes();
        setInterval(checkMedTimes, 30000);
    }})();
    </script>
    """, height=0)
except Exception:
    pass

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'users' not in st.session_state:
    st.session_state.users = []
if 'records' not in st.session_state:
    st.session_state.records = []

# Fetch data
def fetch_data():
    try:
        # Fetch users
        u_resp = requests.get(f"{API_URL}/users", timeout=10)
        if u_resp.status_code == 200:
            st.session_state.users = u_resp.json()
        
        # Fetch records for selected user
        if st.session_state.selected_user:
            r_resp = requests.get(f"{API_URL}/health-data/user/{st.session_state.selected_user}", timeout=10)
            if r_resp.status_code == 200:
                st.session_state.records = r_resp.json()
    except:
        pass

# Initial fetch
fetch_data()

# Sidebar
with st.sidebar:
    st.markdown("## 🏥 Patient Management")
    
    # Patient selection
    if st.session_state.users:
        user_names = [f"{u['name']} (ID: {u['id']})" for u in st.session_state.users]
        selected = st.selectbox("👤 Select Patient", user_names, key="patient_select")
        selected_id = int(selected.split("ID: ")[1].rstrip(")"))
        st.session_state.selected_user = selected_id
        
        selected_name = next(u['name'] for u in st.session_state.users if u['id'] == selected_id)
        st.success(f"✅ Current: {selected_name}")
        
        # Refresh records
        r_resp = requests.get(f"{API_URL}/health-data/user/{selected_id}")
        if r_resp.status_code == 200:
            st.session_state.records = r_resp.json()
        st.info(f"📊 {len(st.session_state.records)} health records")
    
    st.markdown("---")
    
    # Add Patient
    st.markdown("### ➕ Add New Patient")
    new_name = st.text_input("Name", key="new_name")
    new_email = st.text_input("Email", key="new_email")
    if st.button("➕ Add Patient", use_container_width=True):
        if new_name and new_email:
            resp = requests.post(f"{API_URL}/users", json={"name": new_name, "email": new_email})
            if resp.status_code == 200:
                st.success(f"✅ Added {new_name}!")
                fetch_data()
                st.rerun()
    
    st.markdown("---")
    
    # SOS
    st.markdown("### 🚨 Emergency")
    if st.button("🆘 SOS EMERGENCY", use_container_width=True, type="primary"):
        st.error("🚨 SOS ALERT TRIGGERED!")
        if st.session_state.selected_user:
            requests.post(f"{API_URL}/sos", json={"user_id": st.session_state.selected_user})
            st.success("✅ Emergency contacts notified!")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio("📱 Menu", ["📊 Dashboard", "💊 Medications", "🤖 AI Assistant", "📈 Reports"])

# Main content
if st.session_state.selected_user:
    records = st.session_state.records
    
    # DASHBOARD PAGE
    if page == "📊 Dashboard":
        st.title(f"🏥 Welcome, {selected_name}")
        
        if records:
            latest = records[0]
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("❤️ Heart Rate", f"{latest['heart_rate']} bpm", delta="Normal")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💊 Blood Pressure", f"{latest['bp_systolic']}/{latest['bp_diastolic']}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("🩸 Blood Sugar", f"{latest['blood_sugar']} mg/dL")
                st.markdown('</div>', unsafe_allow_html=True)
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("⚖️ Weight", f"{latest['weight']} kg")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No health records found for this patient. Please log new data below to get started.")

        # Log Health Data
        with st.expander("📝 Log New Health Data", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                bp_sys = st.number_input("Systolic BP", 80, 250, 120)
                bp_dia = st.number_input("Diastolic BP", 50, 150, 80)
                hr = st.number_input("Heart Rate", 40, 200, 72)
            with col2:
                sugar = st.number_input("Blood Sugar", 50, 400, 95)
                weight = st.number_input("Weight (kg)", 20.0, 150.0, 70.0)
            
            if st.button("💾 Save Health Record", type="primary"):
                payload = {"user_id": st.session_state.selected_user, "bp_systolic": bp_sys, "bp_diastolic": bp_dia, "heart_rate": hr, "blood_sugar": sugar, "weight": weight}
                resp = requests.post(f"{API_URL}/health-data", json=payload)
                if resp.status_code == 200:
                    st.success("✅ Saved! Refreshing...")
                    fetch_data()
                    st.rerun()
        
        if records:
            # Health History Table
            st.markdown("### 📊 Health History")
            df = pd.DataFrame(records)
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            st.dataframe(df[['recorded_at', 'bp_systolic', 'bp_diastolic', 'heart_rate', 'blood_sugar', 'weight']].head(10), use_container_width=True)
            
            # Trends Chart
            st.markdown("### 📈 Health Trends")
            fig = px.line(df.sort_values('recorded_at'), x='recorded_at', y=['heart_rate', 'blood_sugar'], title='Heart Rate & Blood Sugar Trends')
            st.plotly_chart(fig, use_container_width=True)
        
        # Today's Medications Preview
        st.markdown("### 💊 Today's Medications")
        for med in st.session_state.medications:
            if med["status"] == "pending":
                st.markdown(f"• **{med['name']}** - {med['dosage']} at {med['time']}")
    
    # MEDICATIONS PAGE
    elif page == "💊 Medications":
        st.title(f"💊 Medication Manager - {selected_name}")

        if st.button("🤖 Get AI Medication Suggestions", type="primary"):
            with st.spinner("Analyzing with AI..."):
                med_list = [{"name": m['name'], "dosage": m['dosage'], "type": m['type'], "time": m['time']} for m in st.session_state.medications]
                resp = requests.post(f"{API_URL}/api/ai/medication-suggestions", json={"user_id": st.session_state.selected_user, "medications": med_list})
                if resp.status_code == 200:
                    st.info(resp.json().get("suggestions", "No suggestions received."))
                else:
                    st.error("Failed to fetch AI suggestions.")

        st.markdown("---")
        st.subheader("📋 Current Medications")

        med_types = ["BP", "Diabetes", "Cholesterol", "Pain", "Vitamin", "Antibiotic", "Heart", "Thyroid", "Other"]

        for idx, med in enumerate(st.session_state.medications):
            stock_val = med.get('stock', 0)
            low_stock = stock_val < 5

            with st.expander(
                f"{'🔴' if low_stock else '🟢'} {med['name']}  —  {med['dosage']}  |  ⏰ {med['time']}  |  📦 Stock: {stock_val}  |  {med['status'].upper()}",
                expanded=False
            ):
                ecol1, ecol2, ecol3 = st.columns(3)
                with ecol1:
                    new_name = st.text_input("Medication Name", value=med['name'], key=f"ename_{idx}")
                    new_dosage = st.text_input("Dosage", value=med['dosage'], key=f"edose_{idx}")
                with ecol2:
                    t_parts = med['time'].split(':')
                    edit_hr  = st.number_input("Hour (0-23)",   min_value=0, max_value=23, value=int(t_parts[0]), key=f"ehr_{idx}")
                    edit_min = st.number_input("Minute (0-59)", min_value=0, max_value=59, value=int(t_parts[1]), key=f"emin_{idx}")
                    new_type = st.selectbox("Type", med_types,
                                            index=med_types.index(med['type']) if med['type'] in med_types else len(med_types)-1,
                                            key=f"etype_{idx}")
                with ecol3:
                    new_stock = st.number_input("Stock Quantity", min_value=0, max_value=9999,
                                                value=stock_val, key=f"estock_{idx}")
                    new_status = st.selectbox("Status", ["pending", "taken", "skipped"],
                                              index=["pending", "taken", "skipped"].index(med.get("status", "pending")),
                                              key=f"estatus_{idx}")

                if low_stock:
                    st.error(f"⚠️ Low Stock Warning: Only {stock_val} doses remaining! Please refill soon.")

                btn1, btn2, btn3, btn4, btn5, btn6, btn7 = st.columns(7)
                with btn1:
                    if st.button("💾 Save", key=f"save_{idx}", type="primary"):
                        new_time_str = f"{edit_hr:02d}:{edit_min:02d}"
                        st.session_state.medications[idx].update({
                            "name": new_name, "dosage": new_dosage,
                            "time": new_time_str,
                            "type": new_type, "stock": new_stock, "status": new_status
                        })
                        st.success(f"✅ Alarm set for {new_time_str}")
                        st.rerun()
                with btn2:
                    if med["status"] == "pending":
                        if st.button("✅ Take", key=f"take_{idx}"):
                            st.session_state.medications[idx]["status"] = "taken"
                            if st.session_state.medications[idx].get("stock", 0) > 0:
                                st.session_state.medications[idx]["stock"] -= 1
                            st.rerun()
                with btn3:
                    if med["status"] == "pending":
                        if st.button("⏭️ Skip", key=f"skip_{idx}"):
                            st.session_state.medications[idx]["status"] = "skipped"
                            st.rerun()
                with btn4:
                    if st.button("🔄 Reset", key=f"reset_{idx}"):
                        st.session_state.medications[idx]["status"] = "pending"
                        st.rerun()
                with btn5:
                    if st.button("🔔 Ring Now", key=f"ring_{idx}"):
                        med_data = json.dumps(med)
                        components.html(f"""
                        <script>
                        setTimeout(function() {{
                            try {{
                                if (window.parent && window.parent._triggerMedAlarm) {{
                                    window.parent._triggerMedAlarm({med_data});
                                }} else {{
                                    alert("⏰ Reminder: Take {med['name']} {med['dosage']} now!");
                                }}
                            }} catch(e) {{
                                alert("⏰ Reminder: Take {med['name']} {med['dosage']} now!");
                            }}
                        }}, 300);
                        </script>
                        """, height=0)
                with btn6:
                    if st.button("📱 SMS", key=f"sms_{idx}"):
                        msg = f"Reminder: Take {med['name']} {med['dosage']} at {med['time']}!"
                        requests.post(f"{API_URL}/api/notify", json={"user_id": st.session_state.selected_user, "message": msg, "delivery_type": "sms"})
                        st.toast("📱 SMS Sent!")
                with btn7:
                    if st.button("🗑️ Delete", key=f"del_{idx}"):
                        st.session_state.medications.pop(idx)
                        st.rerun()


        # Add New Medication
        st.markdown("---")
        st.subheader("➕ Add New Medication")
        with st.form("add_med_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_med_name = st.text_input("Medication Name", placeholder="e.g. Aspirin")
                new_dosage = st.text_input("Dosage", placeholder="e.g. 75mg")
                new_stock = st.number_input("Initial Stock Quantity", min_value=1, max_value=1000, value=30)
            with col2:
                c21, c22 = st.columns(2)
                with c21:
                    add_hr  = st.number_input("Hour (0-23)",   min_value=0, max_value=23, value=8)
                with c22:
                    add_min = st.number_input("Minute (0-59)", min_value=0, max_value=59, value=0)
                new_type = st.selectbox("Type", med_types)

            submitted = st.form_submit_button("💊 Add Medication", type="primary", use_container_width=True)
            if submitted:
                if new_med_name and new_dosage:
                    alarm_time = f"{add_hr:02d}:{add_min:02d}"
                    st.session_state.medications.append({
                        "name": new_med_name, "dosage": new_dosage,
                        "time": alarm_time,
                        "status": "pending", "type": new_type, "stock": new_stock
                    })
                    st.success(f"✅ {new_med_name} added! Alarm set for {alarm_time}")
                    st.rerun()
                else:
                    st.error("Please enter Medication Name and Dosage.")

    
    # AI ASSISTANT PAGE
    elif page == "🤖 AI Assistant":
        st.title(f"🤖 AI Health Assistant - {selected_name}")
        
        col1, col2 = st.columns([8, 2])
        with col2:
            if st.button("🗑️ Clear Chat", help="Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

        # Chat display
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a health question..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    resp = requests.post(f"{API_URL}/api/ai/chat", json={"user_id": st.session_state.selected_user, "question": prompt})
                    if resp.status_code == 200:
                        response = resp.json().get("response", "No response retrieved.")
                    else:
                        response = "Error connecting to AI service."
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})        
        # Health Tips
        st.markdown("---")
        st.subheader("💡 Quick Health Tips")
        tips = [
            "🥤 Drink 8 glasses of water daily",
            "🏃‍♂️ Exercise for 30 minutes daily",
            "😴 Get 7-8 hours of sleep",
            "🥗 Eat balanced meals",
            "📊 Track your blood pressure regularly"
        ]
        for tip in tips:
            st.markdown(f"• {tip}")
    
    # REPORTS PAGE
    elif page == "📈 Reports":
        st.title(f"📈 Health Analytics - {selected_name}")
        
        if records:
            df = pd.DataFrame(records)
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            
            # Summary Stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Records", len(df))
            with col2:
                st.metric("❤️ Avg Heart Rate", f"{df['heart_rate'].mean():.0f} bpm")
            with col3:
                st.metric("💊 Avg BP Systolic", f"{df['bp_systolic'].mean():.0f}")
            with col4:
                st.metric("🩸 Avg Blood Sugar", f"{df['blood_sugar'].mean():.0f} mg/dL")
            
            # Full Trends
            fig = px.line(df.sort_values('recorded_at'), x='recorded_at', y=['bp_systolic', 'bp_diastolic', 'heart_rate', 'blood_sugar', 'weight'], title='All Health Metrics Over Time')
            st.plotly_chart(fig, use_container_width=True)
            
            # Export Data
            colA, colB = st.columns(2)
            safe_name = "".join([c if c.isalnum() else "_" for c in selected_name])
            with colA:
                csv = df.to_csv(index=False)
                st.download_button("📥 Download Report (CSV)", csv, file_name=f"{safe_name}_health_report.csv", mime="text/csv", use_container_width=True)
            with colB:
                try:
                    pdf_bytes = create_pdf(df, selected_name, st.session_state.medications)
                    st.download_button("📥 Download Report (PDF)", pdf_bytes, file_name=f"{safe_name}_health_report.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
        else:
            st.info("No data available to generate reports.")

else:
    st.info("Please select a patient from the sidebar")
