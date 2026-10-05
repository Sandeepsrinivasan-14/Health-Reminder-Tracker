"""Health Reminder Tracker: Streamlit frontend.

Run:  streamlit run frontend/streamlit_app.py   (expects the API at $API_URL, default http://127.0.0.1:8000)
"""

from __future__ import annotations

import json
from datetime import time

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from api_client import APIError, HealthAPI

st.set_page_config(page_title="Health Reminder Tracker", page_icon="🩺", layout="wide")

SEVERITY_BADGE = {"normal": "🟢 Normal", "watch": "🟡 Watch", "high": "🟠 High", "urgent": "🔴 Urgent"}
METRIC_LABELS = {"blood_pressure": "Blood pressure", "heart_rate": "Heart rate", "blood_glucose": "Blood glucose", "bmi": "BMI"}
MED_CATEGORIES = ["BP", "Diabetes", "Cholesterol", "Heart", "Thyroid", "Pain", "Vitamin", "Antibiotic", "Other"]


@st.cache_resource
def get_api() -> HealthAPI:
    return HealthAPI()


api = get_api()


def call(fn, *args, **kwargs):
    """Run an API call and show a friendly error instead of a stack trace."""
    try:
        return fn(*args, **kwargs)
    except APIError as exc:
        st.error(f"{exc.detail}")
    except Exception as exc:  # network errors
        st.error(f"Could not reach the API at {api.base_url} ({exc.__class__.__name__}). Is the backend running?")
    return None


# ---------------- Medication alarm (runs in the browser) ----------------


def medication_alarm(pending: list[dict]) -> None:
    """Inject a client-side alarm that rings (beep + speech + modal) when a pending dose is due.

    Data is passed as JSON, never string-interpolated into JS, so medication names cannot inject script.
    """
    payload = json.dumps([{"id": m["id"], "name": m["name"], "dosage": m["dosage"], "time": m["schedule_time"]} for m in pending])
    components.html(
        f"""
<script>
(function() {{
  const meds = {payload};
  const P = window.parent; const D = P.document;
  const key = 'hrt-dismissed-' + new Date().toDateString();
  const dismissed = new Set(JSON.parse(P.localStorage.getItem(key) || '[]'));
  if (!D.getElementById('hrt-alarm')) {{
    const s = D.createElement('style');
    s.textContent = `#hrt-alarm{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:999999;align-items:center;justify-content:center}}
      #hrt-alarm .box{{background:#fff;color:#111;border-radius:16px;padding:32px;max-width:420px;width:90%;text-align:center;font-family:sans-serif}}
      #hrt-alarm h2{{color:#b91c1c;margin:8px 0}} #hrt-alarm button{{border:0;border-radius:10px;padding:12px 20px;margin:8px;font-size:16px;cursor:pointer}}`;
    D.head.appendChild(s);
    const d = D.createElement('div'); d.id = 'hrt-alarm';
    d.innerHTML = '<div class="box"><div style="font-size:48px">💊</div><h2 id="hrt-title"></h2><p id="hrt-body"></p>' +
      '<button id="hrt-ok" style="background:#15803d;color:#fff">Got it</button>' +
      '<button id="hrt-snooze" style="background:#d97706;color:#fff">Snooze 5 min</button></div>';
    D.body.appendChild(d);
  }}
  const modal = D.getElementById('hrt-alarm');
  let current = null, beeper = null; const snoozed = {{}};
  function beep() {{ try {{ const c = new (P.AudioContext || P.webkitAudioContext)();
    [[880,0],[660,.3],[880,.6]].forEach(([f,t]) => {{ const o=c.createOscillator(), g=c.createGain(); o.connect(g); g.connect(c.destination);
      o.frequency.value=f; g.gain.setValueAtTime(.3,c.currentTime+t); g.gain.exponentialRampToValueAtTime(.001,c.currentTime+t+.25);
      o.start(c.currentTime+t); o.stop(c.currentTime+t+.3); }}); }} catch(e) {{}} }}
  function close() {{ modal.style.display='none'; clearInterval(beeper); if (P.speechSynthesis) P.speechSynthesis.cancel(); }}
  D.getElementById('hrt-ok').onclick = () => {{ dismissed.add(current.id); P.localStorage.setItem(key, JSON.stringify([...dismissed])); close(); }};
  D.getElementById('hrt-snooze').onclick = () => {{ snoozed[current.id] = Date.now() + 300000; close(); }};
  function ring(m) {{
    current = m; D.getElementById('hrt-title').textContent = 'Time for ' + m.name;
    D.getElementById('hrt-body').textContent = m.dosage + ' (scheduled ' + m.time + '). Mark it as taken in the app.';
    modal.style.display = 'flex'; beep(); clearInterval(beeper); beeper = setInterval(beep, 4000);
    if (P.speechSynthesis) P.speechSynthesis.speak(new P.SpeechSynthesisUtterance('Time to take ' + m.name + ' ' + m.dosage));
    if (P.Notification && P.Notification.permission === 'granted') new P.Notification('Medication: ' + m.name, {{ body: m.dosage }});
  }}
  P._hrtRing = ring;
  if (P.Notification && P.Notification.permission === 'default') P.Notification.requestPermission();
  function check() {{
    if (modal.style.display === 'flex') return;
    const now = new Date(), mins = now.getHours()*60 + now.getMinutes();
    for (const m of meds) {{
      if (dismissed.has(m.id) || (snoozed[m.id] && Date.now() < snoozed[m.id])) continue;
      const [h, mm] = m.time.split(':').map(Number);
      if (mins >= h*60+mm && mins - (h*60+mm) <= 30) {{ ring(m); break; }}
    }}
  }}
  clearInterval(P._hrtTimer); P._hrtTimer = setInterval(check, 30000); check();
}})();
</script>""",
        height=0,
    )


def ring_now(med: dict) -> None:
    payload = json.dumps({"id": med["id"], "name": med["name"], "dosage": med["dosage"], "time": med["schedule_time"]})
    components.html(
        f"<script>setTimeout(() => window.parent._hrtRing && window.parent._hrtRing({payload}), 200);</script>", height=0
    )


# ---------------- Sidebar: patient selection ----------------

with st.sidebar:
    st.title("🩺 Health Reminder Tracker")
    users = call(api.list_users) or []

    if users:
        labels = {u["id"]: f"{u['name']} ({u['email']})" for u in users}
        default_id = st.session_state.get("patient_id", users[0]["id"])
        if default_id not in labels:
            default_id = users[0]["id"]
        patient_id = st.selectbox("Patient", list(labels), index=list(labels).index(default_id), format_func=labels.__getitem__)
        st.session_state["patient_id"] = patient_id
        patient = next(u for u in users if u["id"] == patient_id)
    else:
        patient = None
        st.info("No patients yet. Add one below.")

    with st.expander("➕ Add patient", expanded=not users):
        with st.form("add_patient", clear_on_submit=True):
            name = st.text_input("Full name")
            email = st.text_input("Email")
            height = st.number_input("Height (cm, optional)", min_value=0.0, max_value=250.0, value=0.0, step=1.0)
            c_phone = st.text_input("Caretaker phone (E.164, e.g. +919876543210)")
            c_email = st.text_input("Caretaker email")
            if st.form_submit_button("Add patient", use_container_width=True):
                data = {
                    "name": name,
                    "email": email,
                    "height_cm": height or None,
                    "caretaker_phone": c_phone or None,
                    "caretaker_email": c_email or None,
                }
                created = call(api.create_user, **data)
                if created:
                    st.session_state["patient_id"] = created["id"]
                    st.rerun()

    page = st.radio("Go to", ["📊 Dashboard", "💊 Medications", "🤖 Assistant", "📄 Reports", "⚙️ Patient settings"])

    if patient:
        st.divider()
        if st.button("🆘 Send SOS to caretaker", type="primary", use_container_width=True):
            st.session_state["confirm_sos"] = True
        if st.session_state.get("confirm_sos"):
            st.warning("Send an emergency alert to the caretaker now?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, send", use_container_width=True):
                results = call(api.sos, patient["id"]) or []
                st.session_state["confirm_sos"] = False
                for r in results:
                    icon = {"sent": "✅", "not_configured": "⚙️", "failed": "❌"}[r["status"]]
                    st.write(f"{icon} {r['channel']}: {r['status'].replace('_', ' ')}")
                st.caption("In a real emergency, call 112.")
            if c2.button("Cancel", use_container_width=True):
                st.session_state["confirm_sos"] = False
                st.rerun()

if not patient:
    st.header("Welcome")
    st.write("Add a patient from the sidebar to start tracking vitals and medications.")
    st.stop()

pid = patient["id"]
medications = call(api.list_medications, pid) or []
medication_alarm([m for m in medications if m["status_today"] == "pending"])


# ---------------- Pages ----------------

if page == "📊 Dashboard":
    st.header(f"Dashboard: {patient['name']}")
    vitals = call(api.list_vitals, pid) or []
    assessment = call(api.assessment, pid) if vitals else None

    if assessment:
        st.subheader(f"Latest status: {SEVERITY_BADGE[assessment['overall']]}")
        if assessment["overall"] == "urgent":
            st.error("At least one reading is in an urgent range. If you feel unwell, seek medical care now (112).")
        cols = st.columns(len(assessment["findings"]))
        for col, f in zip(cols, assessment["findings"]):
            with col:
                value, _, context = f["value"].partition(" (")
                st.metric(METRIC_LABELS.get(f["metric"], f["metric"]), value)
                detail = "" if f["category"] == "Normal" else f" · {f['category']}"
                context = context.rstrip(")")
                if context and context not in f["category"]:
                    detail += f" · {context}"
                st.caption(f"{SEVERITY_BADGE[f['severity']]}{detail}")
        with st.expander("What do these results mean?"):
            for f in assessment["findings"]:
                st.markdown(f"- **{METRIC_LABELS.get(f['metric'], f['metric'])}**: {f['advice']}")
            st.caption(assessment["disclaimer"])
    else:
        st.info("No readings yet. Log the first one below.")

    with st.expander("📝 Log a new reading", expanded=not vitals):
        with st.form("add_vital", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            systolic = c1.number_input("Systolic (mmHg)", 60, 260, 120)
            diastolic = c1.number_input("Diastolic (mmHg)", 30, 160, 80)
            heart_rate = c2.number_input("Resting heart rate (bpm)", 25, 250, 72)
            weight = c2.number_input("Weight (kg)", 2.0, 350.0, 70.0, step=0.1)
            glucose = c3.number_input("Blood glucose (mg/dL)", 20, 600, 95)
            context = c3.selectbox("Glucose taken", ["fasting", "random", "post_meal"], format_func=lambda x: x.replace("_", "-"))
            notes = st.text_input("Notes (optional)")
            if st.form_submit_button("Save reading", type="primary"):
                saved = call(
                    api.add_vital,
                    pid,
                    systolic=systolic,
                    diastolic=diastolic,
                    heart_rate=heart_rate,
                    blood_glucose=glucose,
                    glucose_context=context,
                    weight_kg=weight,
                    notes=notes or None,
                )
                if saved:
                    st.success("Reading saved.")
                    st.rerun()

    if vitals:
        df = pd.DataFrame(vitals)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"])
        df = df.sort_values("recorded_at")
        st.subheader("Trends")
        t1, t2, t3 = st.tabs(["Blood pressure", "Glucose & heart rate", "Weight"])
        with t1:
            fig = px.line(
                df, x="recorded_at", y=["systolic", "diastolic"], markers=True, labels={"value": "mmHg", "recorded_at": ""}
            )
            fig.add_hline(y=130, line_dash="dot", annotation_text="130 systolic")
            fig.add_hline(y=80, line_dash="dot", annotation_text="80 diastolic")
            st.plotly_chart(fig, use_container_width=True)
        with t2:
            st.plotly_chart(
                px.line(df, x="recorded_at", y=["blood_glucose", "heart_rate"], markers=True, labels={"recorded_at": ""}),
                use_container_width=True,
            )
        with t3:
            st.plotly_chart(
                px.line(df, x="recorded_at", y="weight_kg", markers=True, labels={"recorded_at": ""}), use_container_width=True
            )

        st.subheader("History")
        table = df.sort_values("recorded_at", ascending=False)[
            ["recorded_at", "systolic", "diastolic", "heart_rate", "blood_glucose", "glucose_context", "weight_kg", "notes"]
        ]
        st.dataframe(table, use_container_width=True, hide_index=True)

    st.subheader("Today's medications")
    if not medications:
        st.caption("None scheduled.")
    for m in medications:
        icon = {"pending": "⏳", "taken": "✅", "skipped": "⏭️"}[m["status_today"]]
        st.write(f"{icon} **{m['schedule_time']}**  {m['name']} {m['dosage']}" + ("  ·  ⚠️ low stock" if m["low_stock"] else ""))


elif page == "💊 Medications":
    st.header(f"Medications: {patient['name']}")
    st.caption("Reminders ring in this browser tab while it is open. SMS/email reminders go to the caretaker on file.")

    for m in medications:
        status = {"pending": "⏳ pending", "taken": "✅ taken", "skipped": "⏭️ skipped"}[m["status_today"]]
        stock = f"⚠️ {m['stock']} left" if m["low_stock"] else f"{m['stock']} left"
        with st.expander(f"{m['schedule_time']} · {m['name']} {m['dosage']} · {status} · {stock}"):
            b = st.columns(5)
            if b[0].button("✅ Taken", key=f"take{m['id']}", disabled=m["status_today"] != "pending"):
                if call(api.log_dose, m["id"], "taken"):
                    st.rerun()
            if b[1].button("⏭️ Skip", key=f"skip{m['id']}", disabled=m["status_today"] != "pending"):
                if call(api.log_dose, m["id"], "skipped"):
                    st.rerun()
            if b[2].button("🔔 Test alarm", key=f"ring{m['id']}"):
                ring_now(m)
            channel = b[3].selectbox("Channel", ["sms", "whatsapp", "email"], key=f"ch{m['id']}", label_visibility="collapsed")
            if b[4].button("📨 Remind caretaker", key=f"rem{m['id']}"):
                r = call(api.remind, m["id"], channel)
                if r:
                    st.info(
                        f"{r['channel']}: {r['status'].replace('_', ' ')}"
                        + (f" ({r['detail']})" if r["status"] != "sent" else "")
                    )

            with st.form(f"edit{m['id']}"):
                c1, c2, c3 = st.columns(3)
                name = c1.text_input("Name", m["name"])
                dosage = c1.text_input("Dosage", m["dosage"])
                hh, mm = map(int, m["schedule_time"].split(":"))
                at = c2.time_input("Time", time(hh, mm), step=300)
                category = c2.selectbox(
                    "Category",
                    MED_CATEGORIES,
                    index=MED_CATEGORIES.index(m["category"]) if m["category"] in MED_CATEGORIES else 8,
                )
                stock_val = c3.number_input("Stock", 0, 10000, m["stock"])
                threshold = c3.number_input("Low-stock alert at", 0, 1000, m["low_stock_threshold"])
                s1, s2 = st.columns(2)
                if s1.form_submit_button("Save changes"):
                    if call(
                        api.update_medication,
                        m["id"],
                        name=name,
                        dosage=dosage,
                        schedule_time=at.strftime("%H:%M"),
                        category=category,
                        stock=stock_val,
                        low_stock_threshold=threshold,
                    ):
                        st.rerun()
                if s2.form_submit_button("Delete medication"):
                    call(api.delete_medication, m["id"])
                    st.rerun()

    st.subheader("Add a medication")
    with st.form("add_med", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Name", placeholder="e.g. Amlodipine")
        dosage = c1.text_input("Dosage", placeholder="e.g. 5 mg")
        at = c2.time_input("Time", time(8, 0), step=300)
        category = c2.selectbox("Category", MED_CATEGORIES)
        stock_val = c3.number_input("Current stock", 0, 10000, 30)
        threshold = c3.number_input("Low-stock alert at", 0, 1000, 5)
        if st.form_submit_button("Add medication", type="primary"):
            if call(
                api.add_medication,
                pid,
                name=name,
                dosage=dosage,
                schedule_time=at.strftime("%H:%M"),
                category=category,
                stock=stock_val,
                low_stock_threshold=threshold,
            ):
                st.rerun()


elif page == "🤖 Assistant":
    st.header("Health assistant")
    st.caption("Explains your readings in plain language. It does not diagnose or change your treatment; ask your doctor.")
    history = st.session_state.setdefault(f"chat_{pid}", [])
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if question := st.chat_input("Ask about your readings, e.g. 'Is my blood pressure OK?'"):
        history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = call(api.chat, pid, question)
            text = reply["answer"] if reply else "Sorry, I couldn't get an answer right now."
            st.markdown(text)
            if reply and reply["source"] == "rules":
                st.caption("Answered by the built-in rule engine (no LLM key configured).")
        history.append({"role": "assistant", "content": text})

    st.divider()
    if st.button("💡 Get personalised tips"):
        tips = call(api.tips, pid)
        if tips:
            for t in tips["tips"]:
                st.markdown(f"- {t}")


elif page == "📄 Reports":
    st.header(f"Reports: {patient['name']}")
    st.write("Download a summary to share with your doctor.")
    c1, c2 = st.columns(2)
    pdf = call(api.report_pdf, pid)
    if pdf:
        c1.download_button(
            "📄 Download PDF report", pdf, file_name=f"health_report_{pid}.pdf", mime="application/pdf", use_container_width=True
        )
    csv = call(api.report_csv, pid)
    if csv:
        c2.download_button(
            "📊 Download readings (CSV)", csv, file_name=f"vitals_{pid}.csv", mime="text/csv", use_container_width=True
        )
    st.subheader("Alert history")
    alerts = call(api.list_alerts, pid) or []
    if alerts:
        st.dataframe(
            pd.DataFrame(alerts)[["created_at", "kind", "channel", "status", "detail"]], hide_index=True, use_container_width=True
        )
    else:
        st.caption("No alerts sent yet.")


elif page == "⚙️ Patient settings":
    st.header("Patient settings")
    with st.form("edit_patient"):
        name = st.text_input("Full name", patient["name"])
        height = st.number_input("Height (cm)", 0.0, 250.0, float(patient["height_cm"] or 0), step=1.0)
        c_name = st.text_input("Caretaker name", patient["caretaker_name"] or "")
        c_phone = st.text_input("Caretaker phone (E.164)", patient["caretaker_phone"] or "")
        c_email = st.text_input("Caretaker email", patient["caretaker_email"] or "")
        if st.form_submit_button("Save", type="primary"):
            if call(
                api.update_user,
                pid,
                name=name,
                height_cm=height or None,
                caretaker_name=c_name or None,
                caretaker_phone=c_phone or None,
                caretaker_email=c_email or None,
            ):
                st.success("Saved.")
                st.rerun()
    with st.expander("Danger zone"):
        st.write("Deleting a patient removes all of their readings, medications and alerts.")
        if st.checkbox("I understand this cannot be undone"):
            if st.button("Delete patient", type="primary"):
                call(api.delete_user, pid)
                st.session_state.pop("patient_id", None)
                st.rerun()
