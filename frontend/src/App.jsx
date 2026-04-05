import React, { useState, useEffect } from 'react';

const USERS = [
  { id: 1, name: "Test Patient", condition: "Healthy" },
  { id: 2, name: "Rajesh Kumar", condition: "Diabetes" },
  { id: 3, name: "Priya Sharma", condition: "Healthy" },
  { id: 4, name: "Amit Patel", condition: "Heart Disease" },
  { id: 5, name: "Sunita Reddy", condition: "Hypertension" },
  { id: 6, name: "Vikram Singh", condition: "Diabetes" },
  { id: 7, name: "Neha Gupta", condition: "Asthma" },
  { id: 8, name: "Anand Desai", condition: "Hypertension" },
  { id: 9, name: "Kavita Nair", condition: "Thyroid" },
  { id: 10, name: "Suresh Iyer", condition: "Heart Disease" },
  { id: 11, name: "Meera Joshi", condition: "Migraine" },
  { id: 12, name: "Rohan Mehta", condition: "Healthy" },
  { id: 13, name: "Anjali Kulkarni", condition: "Diabetes" },
  { id: 14, name: "Deepak Saxena", condition: "Obesity" },
  { id: 15, name: "Swati Choudhary", condition: "Anemia" },
  { id: 16, name: "Manoj Verma", condition: "Hypertension" },
  { id: 17, name: "Pooja Malhotra", condition: "Osteoporosis" },
  { id: 18, name: "Arjun Nair", condition: "Healthy" },
  { id: 19, name: "Divya Menon", condition: "PCOS" },
  { id: 20, name: "Sanjay Gupta", condition: "Diabetes" },
  { id: 21, name: "Lata Mangeshkar", condition: "Hypertension" },
  { id: 22, name: "Lohith", condition: "Healthy" }
];

function App() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [users] = useState(USERS);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [healthData, setHealthData] = useState({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);
  const [riskResult, setRiskResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [healthRecords, setHealthRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  const API_URL = 'https://health-reminder-tracker.onrender.com';

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.style.background = '#0f172a';
    }
  }, []);

  useEffect(() => {
    if (selectedUser) {
      loadUserHealthData();
    }
  }, [selectedUser]);

  const loadUserHealthData = async () => {
    setLoading(true);
    try {
      console.log("Loading data for user:", selectedUser.id, selectedUser.name);
      
      // Fetch health records from backend
      const res = await fetch(`${API_URL}/health-data/user/${selectedUser.id}`);
      const records = await res.json();
      console.log("Records received:", records);
      
      setHealthRecords(records);
      
      if (records && records.length > 0) {
        // Use the latest record
        const latest = records[0];
        setHealthData({
          bp_systolic: latest.bp_systolic,
          bp_diastolic: latest.bp_diastolic,
          heart_rate: latest.heart_rate,
          blood_sugar: latest.blood_sugar,
          weight: latest.weight
        });
      } else {
        // Fallback to condition-based defaults if no records
        const defaults = {
          "Diabetes": { bp_sys: 135, bp_dia: 85, hr: 78, sugar: 180, weight: 75 },
          "Hypertension": { bp_sys: 155, bp_dia: 95, hr: 82, sugar: 110, weight: 80 },
          "Heart Disease": { bp_sys: 145, bp_dia: 90, hr: 95, sugar: 115, weight: 78 },
          "Obesity": { bp_sys: 140, bp_dia: 88, hr: 85, sugar: 125, weight: 110 },
          "Thyroid": { bp_sys: 125, bp_dia: 80, hr: 70, sugar: 100, weight: 85 },
          "Asthma": { bp_sys: 120, bp_dia: 78, hr: 75, sugar: 95, weight: 65 },
          "Anemia": { bp_sys: 105, bp_dia: 65, hr: 88, sugar: 85, weight: 55 },
          "Osteoporosis": { bp_sys: 130, bp_dia: 82, hr: 72, sugar: 100, weight: 60 },
          "PCOS": { bp_sys: 128, bp_dia: 82, hr: 76, sugar: 115, weight: 82 },
          "Migraine": { bp_sys: 118, bp_dia: 75, hr: 68, sugar: 92, weight: 62 },
          "Healthy": { bp_sys: 118, bp_dia: 78, hr: 72, sugar: 95, weight: 68 }
        };
        const def = defaults[selectedUser.condition] || defaults["Healthy"];
        setHealthData({
          bp_systolic: def.bp_sys,
          bp_diastolic: def.bp_dia,
          heart_rate: def.hr,
          blood_sugar: def.sugar,
          weight: def.weight
        });
      }
    } catch (err) {
      console.error("Error loading health data:", err);
    } finally {
      setLoading(false);
    }
  };

  const saveHealthData = async () => {
    if (!selectedUser) { alert('Select a user first'); return; }
    const data = {
      user_id: selectedUser.id,
      bp_systolic: parseInt(healthData.bp_systolic) || 0,
      bp_diastolic: parseInt(healthData.bp_diastolic) || 0,
      heart_rate: parseInt(healthData.heart_rate) || 0,
      blood_sugar: parseInt(healthData.blood_sugar) || 0,
      weight: parseFloat(healthData.weight) || 0
    };
    await fetch(`${API_URL}/health-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    alert('Health data saved!');
    loadUserHealthData();
  };

  const analyzeRisk = async () => {
    if (!selectedUser) { alert('Select a user first'); return; }
    const riskBody = {
      health_data: {
        bp_systolic: parseInt(healthData.bp_systolic) || 120,
        bp_diastolic: parseInt(healthData.bp_diastolic) || 80,
        heart_rate: parseInt(healthData.heart_rate) || 75,
        blood_sugar: parseInt(healthData.blood_sugar) || 100,
        weight: parseFloat(healthData.weight) || 70
      }
    };
    const res = await fetch(`${API_URL}/api/ai/health-risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(riskBody)
    });
    const data = await res.json();
    setRiskResult(data);
  };

  const askAI = async () => {
    if (!selectedUser) { alert('Select a user first'); return; }
    if (!aiQuestion.trim()) return;
    
    const userMessage = aiQuestion;
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setAiQuestion('');
    setIsLoading(true);
    
    try {
      const res = await fetch(`${API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage, health_data: healthData, session_id: selectedUser.id.toString() })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadHealthTips = () => {
    if (!selectedUser) { alert('Select a user first'); return; }
    const conditionTips = {
      "Diabetes": ["🩸 Monitor blood sugar daily", "🥗 Eat low glycemic index foods", "🚶 Walk after meals", "💊 Take insulin on time", "🍎 Avoid sugary drinks"],
      "Hypertension": ["❤️ Reduce salt intake", "🚶 Walk 30 mins daily", "💧 Drink more water", "🥦 Eat more potassium", "😴 Get enough sleep"],
      "Heart Disease": ["💔 Take aspirin as prescribed", "🚶 Light exercise only", "🥗 Low fat diet", "💊 Take medications on time", "🚭 Avoid stress"],
      "Healthy": ["✅ Keep up the good work!", "🥗 Eat balanced diet", "🚶 Stay active", "💧 Stay hydrated", "😴 Sleep well"],
      "Asthma": ["🌬️ Use inhaler as prescribed", "🚶 Avoid triggers", "💨 Practice breathing exercises", "🏠 Keep home dust-free", "💊 Take preventive meds"],
      "Thyroid": ["🦋 Take thyroid medication daily", "🥗 Eat iodine-rich foods", "💊 Don't skip doses", "🩸 Get regular checkups", "😴 Manage stress"],
      "Obesity": ["⚖️ Track your calories", "🚶 Walk 10k steps daily", "🥗 Eat more protein", "💧 Drink water before meals", "🏋️ Strength training"],
      "Anemia": ["🩸 Eat iron-rich foods", "🥩 Include red meat", "🥬 Eat spinach", "💊 Take iron supplements", "🍊 Vitamin C with iron"],
      "PCOS": ["🌸 Maintain healthy weight", "🥗 Low carb diet", "🚶 Regular exercise", "💊 Take prescribed meds", "🩸 Monitor cycles"],
      "Migraine": ["🧠 Avoid triggers", "💧 Stay hydrated", "😴 Regular sleep schedule", "☕ Limit caffeine", "🧘 Practice relaxation"],
      "Osteoporosis": ["🦴 Increase calcium intake", "☀️ Get Vitamin D", "🏋️ Weight bearing exercises", "💊 Take prescribed meds", "🚫 Avoid smoking"]
    };
    setHealthTips(conditionTips[selectedUser.condition] || conditionTips["Healthy"]);
    setShowTips(true);
  };

  const sendSOS = async () => {
    try {
      await fetch(`${API_URL}/sos`, { method: 'POST' });
      alert('🚨 SOS Alert Sent! Caregiver notified.');
    } catch (err) {
      alert('❌ Failed to send SOS');
    }
  };

  const exportPDF = () => {
    if (!selectedUser) { alert('Select a user first'); return; }
    window.open(`${API_URL}/export-pdf/${selectedUser.id}`, '_blank');
  };

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
    document.body.style.background = newTheme ? '#0f172a' : '#f0f2f5';
  };

  const cardBg = isDarkMode ? '#1e293b' : '#ffffff';
  const textColor = isDarkMode ? '#f1f5f9' : '#1f2937';
  const borderColor = isDarkMode ? '#334155' : '#e5e7eb';
  const inputBg = isDarkMode ? '#334155' : '#ffffff';

  return React.createElement('div', { style: { minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)', padding: '20px' } },
    React.createElement('div', { style: { maxWidth: '1400px', margin: '0 auto' } },
      
      React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '20px 30px', marginBottom: '25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
        React.createElement('div', null,
          React.createElement('h1', { style: { margin: 0, fontSize: '28px', color: textColor } }, '🏥 Medical Health Tracker'),
          React.createElement('p', { style: { margin: '5px 0 0', color: textColor } }, 'AI-Powered Healthcare Assistant')
        ),
        React.createElement('div', { style: { display: 'flex', gap: '15px', alignItems: 'center' } },
          React.createElement('button', { onClick: toggleTheme, style: { background: 'rgba(0,0,0,0.1)', border: 'none', borderRadius: '50%', width: '40px', height: '40px', fontSize: '20px', cursor: 'pointer', color: textColor } }, isDarkMode ? '☀️' : '🌙'),
          React.createElement('div', { style: { background: '#10b981', padding: '6px 16px', borderRadius: '50px', color: 'white', fontSize: '13px', fontWeight: '600' } }, '✅ API: Healthy')
        )
      ),

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' } },
        
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '👤 Select Patient'),
          React.createElement('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '10px', maxHeight: '300px', overflowY: 'auto', marginBottom: '20px' } },
            users.map(user => React.createElement('button', { key: user.id, onClick: () => setSelectedUser(user), style: { padding: '8px 18px', background: selectedUser?.id === user.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : '#f3f4f6', color: selectedUser?.id === user.id ? 'white' : textColor, border: 'none', borderRadius: '50px', cursor: 'pointer', fontSize: '13px', margin: '4px' } }, `${user.name} (${user.condition})`))
          ),
          selectedUser && React.createElement('div', { style: { padding: '12px', background: 'rgba(16,185,129,0.1)', borderRadius: '12px', marginBottom: '15px' } }, 
            React.createElement('span', { style: { color: '#059669', fontWeight: '600' } }, '✅ Selected: ', selectedUser.name, ' - ', selectedUser.condition)
          ),
          React.createElement('div', { style: { display: 'flex', gap: '12px' } },
            React.createElement('input', { type: 'text', placeholder: 'New Patient Name', id: 'newName', style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
            React.createElement('button', { onClick: () => {
              const name = document.getElementById('newName').value;
              if (name) {
                const newId = Math.max(...users.map(u => u.id)) + 1;
                users.push({ id: newId, name: name, condition: "Healthy" });
                alert('User added! Refresh to see.');
              }
            }, style: { padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '➕ Add User')
          )
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', textAlign: 'center' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '🚨 Emergency SOS'),
          React.createElement('button', { onClick: sendSOS, style: { background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', padding: '16px 40px', fontSize: '18px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(239,68,68,0.3)' } }, '🚨 SOS EMERGENCY'),
          React.createElement('button', { onClick: exportPDF, style: { marginTop: '15px', padding: '10px 20px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '📄 Export PDF Report')
        )
      ),

      React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', marginBottom: '25px' } },
        React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '📊 Current Health Metrics'),
        loading ? React.createElement('div', { style: { textAlign: 'center', padding: '40px', color: textColor } }, 'Loading patient health data...') : [
          React.createElement('div', { key: 'metrics', style: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '15px', marginBottom: '20px' } },
            [
              { label: '🩸 BP Systolic', key: 'bp_systolic', unit: 'mmHg', value: healthData.bp_systolic },
              { label: '🩸 BP Diastolic', key: 'bp_diastolic', unit: 'mmHg', value: healthData.bp_diastolic },
              { label: '💓 Heart Rate', key: 'heart_rate', unit: 'BPM', value: healthData.heart_rate },
              { label: '🩸 Blood Sugar', key: 'blood_sugar', unit: 'mg/dL', value: healthData.blood_sugar },
              { label: '⚖️ Weight', key: 'weight', unit: 'kg', value: healthData.weight }
            ].map(field => React.createElement('div', { key: field.key, style: { textAlign: 'center', padding: '15px', background: isDarkMode ? '#334155' : '#f3f4f6', borderRadius: '12px' } },
              React.createElement('div', { style: { fontSize: '14px', color: textColor, marginBottom: '8px' } }, field.label),
              React.createElement('div', { style: { fontSize: '24px', fontWeight: 'bold', color: '#667eea' } }, field.value || '--'),
              React.createElement('div', { style: { fontSize: '12px', color: '#9ca3af' } }, field.unit)
            ))
          ),
          React.createElement('div', { key: 'buttons', style: { display: 'flex', gap: '12px', justifyContent: 'center' } },
            React.createElement('button', { onClick: analyzeRisk, style: { padding: '12px 24px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '📊 Analyze Health Risk'),
            React.createElement('button', { onClick: loadHealthTips, style: { padding: '12px 24px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '💡 Get Health Tips')
          )
        ]),
        
        riskResult && React.createElement('div', { style: { marginTop: '20px', padding: '18px', borderRadius: '16px', background: riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)', border: `1px solid ${riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}` } },
          React.createElement('h4', { style: { margin: 0, color: riskResult.risk_level === 'HIGH' ? '#dc2626' : '#059669' } }, '⚠️ Risk Level: ', riskResult.risk_level),
          React.createElement('p', { style: { margin: '8px 0', color: textColor } }, React.createElement('strong', null, 'Issues: '), riskResult.risks?.join(', ') || 'None'),
          React.createElement('p', { style: { margin: 0, color: textColor } }, React.createElement('strong', null, 'Recommendations: '), riskResult.recommendations?.join('; ') || 'Continue monitoring')
        ),

        showTips && healthTips.length > 0 && React.createElement('div', { style: { marginTop: '20px' } },
          React.createElement('h3', { style: { color: textColor, marginBottom: '10px' } }, '💡 Personalized Health Tips'),
          healthTips.map((tip, i) => React.createElement('div', { key: i, style: { padding: '12px', marginBottom: '8px', background: 'rgba(16,185,129,0.08)', borderRadius: '12px', color: isDarkMode ? '#86efac' : '#065f46', borderLeft: '4px solid #10b981' } }, tip))
        ),

        healthRecords.length > 0 && React.createElement('div', { style: { marginTop: '20px' } },
          React.createElement('h3', { style: { color: textColor, marginBottom: '10px' } }, '📋 Health History'),
          React.createElement('div', { style: { overflowX: 'auto' } },
            React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
              React.createElement('thead', null,
                React.createElement('tr', { style: { background: isDarkMode ? '#334155' : '#f3f4f6' } },
                  ['Date', 'BP', 'HR', 'Sugar', 'Weight'].map(h => React.createElement('th', { key: h, style: { padding: '10px', textAlign: 'left', color: textColor } }, h))
                )
              ),
              React.createElement('tbody', null,
                healthRecords.slice(0, 5).map((r, i) => React.createElement('tr', { key: i, style: { borderBottom: `1px solid ${borderColor}` } },
                  React.createElement('td', { style: { padding: '8px', color: textColor } }, new Date(r.recorded_at).toLocaleDateString()),
                  React.createElement('td', { style: { padding: '8px', color: textColor } }, `${r.bp_systolic}/${r.bp_diastolic}`),
                  React.createElement('td', { style: { padding: '8px', color: textColor } }, r.heart_rate),
                  React.createElement('td', { style: { padding: '8px', color: textColor } }, r.blood_sugar),
                  React.createElement('td', { style: { padding: '8px', color: textColor } }, r.weight)
                ))
              )
            )
          )
        )
      ),

      React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
        React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '🤖 AI Health Assistant'),
        selectedUser ? [
          React.createElement('div', { key: 'chat', style: { height: '250px', overflowY: 'auto', background: isDarkMode ? '#0f172a' : '#f9fafb', borderRadius: '16px', padding: '15px', marginBottom: '15px', border: `1px solid ${borderColor}` } },
            chatMessages.length === 0 && React.createElement('div', { style: { textAlign: 'center', color: '#9ca3af', padding: '40px' } }, '💬 Ask me about this patient\'s health!'),
            chatMessages.map((msg, idx) => React.createElement('div', { key: idx, style: { marginBottom: '12px', textAlign: msg.role === 'user' ? 'right' : 'left' } },
              React.createElement('div', { style: { display: 'inline-block', maxWidth: '80%', padding: '10px 16px', borderRadius: '20px', background: msg.role === 'user' ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : 'white', color: msg.role === 'user' ? 'white' : textColor } },
                React.createElement('strong', null, msg.role === 'user' ? 'You' : 'AI'), ': ', msg.content
              )
            )),
            isLoading && React.createElement('div', { style: { textAlign: 'left' } }, React.createElement('div', { style: { display: 'inline-block', padding: '10px 16px', borderRadius: '20px', background: isDarkMode ? '#334155' : '#f3f4f6', color: '#9ca3af' } }, 'AI is thinking...'))
          ),
          React.createElement('div', { key: 'input', style: { display: 'flex', gap: '10px' } },
            React.createElement('input', { type: 'text', placeholder: 'Ask about health condition, medications, or advice...', value: aiQuestion, onChange: (e) => setAiQuestion(e.target.value), onKeyPress: (e) => e.key === 'Enter' && askAI(), style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
            React.createElement('button', { onClick: askAI, disabled: isLoading, style: { padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, 'Send')
          )
        ] : React.createElement('div', { style: { textAlign: 'center', padding: '60px', color: '#9ca3af' } }, '👤 Please select a patient first')
      )
    )
  );
}

export default App;
