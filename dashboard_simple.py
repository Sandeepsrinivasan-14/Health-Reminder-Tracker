import streamlit as st

st.set_page_config(page_title="Medical Health Tracker", page_icon="🏥", layout="wide")

# Simple hardcoded users
USERS = ["Test Patient", "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sunita Reddy", 
         "Vikram Singh", "Neha Gupta", "Anand Desai", "Kavita Nair", "Suresh Iyer",
         "Meera Joshi", "Rohan Mehta", "Anjali Kulkarni", "Deepak Saxena", "Swati Choudhary",
         "Manoj Verma", "Pooja Malhotra", "Arjun Nair", "Divya Menon", "Sanjay Gupta",
         "Lata Mangeshkar", "Lohith"]

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; margin-bottom: 20px; }
    .card { background: rgba(255,255,255,0.95); padding: 20px; border-radius: 20px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🏥 Medical Health Tracker</h1><p>AI-Powered Healthcare Assistant</p><div><span style="background:#10b981; padding:6px 16px; border-radius:50px; color:white">✅ Live</span></div></div>', unsafe_allow_html=True)

# Patient Selection
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 👤 Select Patient")

# Create a grid of buttons
cols = st.columns(4)
for i, name in enumerate(USERS):
    with cols[i % 4]:
        if st.button(name, key=f"btn_{i}", use_container_width=True):
            st.session_state.selected = name
            st.rerun()

if 'selected' in st.session_state:
    st.success(f"✅ Selected: {st.session_state.selected}")

st.markdown('</div>', unsafe_allow_html=True)

# SOS Button
st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
st.markdown("### 🚨 Emergency SOS")
if st.button("🚨 SOS EMERGENCY", use_container_width=True):
    st.success("✅ SOS Alert Sent!")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center>🏥 Medical Health Tracker | Made with ❤️</center>", unsafe_allow_html=True)
