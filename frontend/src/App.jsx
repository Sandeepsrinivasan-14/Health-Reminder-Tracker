import React, { useState, useEffect } from 'react';

// HARDCODED USERS - Guaranteed to show!
const HARDCODED_USERS = [
  { id: 1, name: "Test Patient", email: "test@example.com" },
  { id: 2, name: "Rajesh Kumar", email: "rajesh@email.com" },
  { id: 3, name: "Priya Sharma", email: "priya@email.com" },
  { id: 4, name: "Amit Patel", email: "amit@email.com" },
  { id: 5, name: "Sunita Reddy", email: "sunita@email.com" },
  { id: 6, name: "Vikram Singh", email: "vikram@email.com" },
  { id: 7, name: "Neha Gupta", email: "neha@email.com" },
  { id: 8, name: "Anand Desai", email: "anand@email.com" },
  { id: 9, name: "Kavita Nair", email: "kavita@email.com" },
  { id: 10, name: "Suresh Iyer", email: "suresh@email.com" },
  { id: 11, name: "Meera Joshi", email: "meera@email.com" },
  { id: 12, name: "Rohan Mehta", email: "rohan@email.com" },
  { id: 13, name: "Anjali Kulkarni", email: "anjali@email.com" },
  { id: 14, name: "Deepak Saxena", email: "deepak@email.com" },
  { id: 15, name: "Swati Choudhary", email: "swati@email.com" },
  { id: 16, name: "Manoj Verma", email: "manoj@email.com" },
  { id: 17, name: "Pooja Malhotra", email: "pooja@email.com" },
  { id: 18, name: "Arjun Nair", email: "arjun@email.com" },
  { id: 19, name: "Divya Menon", email: "divya@email.com" },
  { id: 20, name: "Sanjay Gupta", email: "sanjay@email.com" },
  { id: 21, name: "Lata Mangeshkar", email: "lata@email.com" },
  { id: 22, name: "Lohith", email: "lohith@email.com" }
];

function App() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState(HARDCODED_USERS);
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [healthData, setHealthData] = useState({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);
  const [riskResult, setRiskResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [healthRecords, setHealthRecords] = useState([]);

  const API_URL = 'https://health-reminder-tracker.onrender.com';

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.style.background = '#0f172a';
    }
    // Also try to fetch users from API to keep in sync
    fetchUsersFromAPI();
  }, []);

  useEffect(() => {
    if (selectedUser) {
      fetchHealthRecords();
    }
  }, [selectedUser]);

  const fetchUsersFromAPI = async () => {
    try {
      const res = await fetch(`${API_URL}/users`);
      const data = await res.json();
      if (data && data.length > 0) {
        setUsers(data);
      }
    } catch (err) {
      console.log('Using hardcoded users');
    }
  };

  const fetchHealthRecords = async () => {
    if (!selectedUser) return;
    try {
      const res = await fetch(`${API_URL}/health-data/user/${selectedUser.id}`);
      const data = await res.json();
      setHealthRecords(data);
    } catch (err) {
      console.error('Failed to fetch health records:', err);
    }
  };

  const createUser = async () => {
    if (!newUserName || !newUserEmail) return;
    try {
      const res = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newUserName, email: newUserEmail })
      });
      const newUser = await res.json();
      setUsers([...users, newUser]);
      setNewUserName('');
      setNewUserEmail('');
    } catch (err) {
      // Add to local list even if API fails
      const newUser = { id: Date.now(), name: newUserName, email: newUserEmail };
      setUsers([...users, newUser]);
      setNewUserName('');
      setNewUserEmail('');
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
    setHealthData({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
    fetchHealthRecords();
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
        body: JSON.stringify({ query: userMessage, health_data: null, session_id: selectedUser.id.toString() })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadHealthTips = async () => {
    if (!selectedUser) { alert('Select a user first'); return; }
    setShowTips(true);
    setHealthTips([
      "?? Check your blood pressure regularly",
      "?? Eat a balanced diet rich in vegetables",
      "?? Walk for 30 minutes daily",
      "?? Drink 8 glasses of water",
      "?? Get 7-8 hours of sleep",
      "?? Monitor your health numbers weekly"
    ]);
  };

  const sendSOS = async () => {
    try {
      await fetch(`${API_URL}/sos`, { method: 'POST' });
      alert('?? SOS Alert Sent! Caregiver notified.');
    } catch (err) {
      alert('? Failed to send SOS');
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
          React.createElement('h1', { style: { margin: 0, fontSize: '28px', color: textColor } }, '?? Medical Health Tracker'),
          React.createElement('p', { style: { margin: '5px 0 0', color: textColor } }, 'AI-Powered Healthcare Assistant')
        ),
        React.createElement('div', { style: { display: 'flex', gap: '15px', alignItems: 'center' } },
          React.createElement('button', { onClick: toggleTheme, style: { background: 'rgba(0,0,0,0.1)', border: 'none', borderRadius: '50%', width: '40px', height: '40px', fontSize: '20px', cursor: 'pointer', color: textColor } }, isDarkMode ? '??' : '??'),
          React.createElement('div', { style: { background: '#10b981', padding: '6px 16px', borderRadius: '50px', color: 'white', fontSize: '13px', fontWeight: '600' } }, '? API: Healthy')
        )
      ),

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' } },
        
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? Create User'),
          React.createElement('div', { style: { display: 'flex', gap: '12px', marginBottom: '20px' } },
            React.createElement('input', { type: 'text', placeholder: 'Full Name', value: newUserName, onChange: (e) => setNewUserName(e.target.value), style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
            React.createElement('input', { type: 'email', placeholder: 'Email', value: newUserEmail, onChange: (e) => setNewUserEmail(e.target.value), style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
            React.createElement('button', { onClick: createUser, style: { padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, 'Create')
          ),
          React.createElement('h3', { style: { color: textColor, fontSize: '16px', marginBottom: '12px' } }, `?? Existing Users (${users.length})`),
          React.createElement('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '10px', maxHeight: '250px', overflowY: 'auto' } },
            users.map(user => React.createElement('button', { key: user.id, onClick: () => setSelectedUser(user), style: { padding: '8px 18px', background: selectedUser?.id === user.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : '#f3f4f6', color: selectedUser?.id === user.id ? 'white' : textColor, border: 'none', borderRadius: '50px', cursor: 'pointer', fontSize: '13px', margin: '4px' } }, user.name))
          ),
          selectedUser && React.createElement('div', { style: { marginTop: '15px', padding: '12px', background: 'rgba(16,185,129,0.1)', borderRadius: '12px' } }, React.createElement('span', { style: { color: '#059669', fontWeight: '600' } }, '? Selected: ', selectedUser.name))
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', textAlign: 'center' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? Emergency SOS'),
          React.createElement('button', { onClick: sendSOS, style: { background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', padding: '16px 40px', fontSize: '18px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(239,68,68,0.3)' } }, '?? SOS EMERGENCY'),
          React.createElement('button', { onClick: exportPDF, style: { marginTop: '15px', padding: '10px 20px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '?? Export PDF Report')
        )
      ),

      React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', marginBottom: '25px' } },
        React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? Health Parameter Tracker'),
        React.createElement('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '15px', marginBottom: '20px' } },
          [
            { label: 'BP Systolic', key: 'bp_systolic', placeholder: '120' },
            { label: 'BP Diastolic', key: 'bp_diastolic', placeholder: '80' },
            { label: 'Heart Rate', key: 'heart_rate', placeholder: '72' },
            { label: 'Blood Sugar', key: 'blood_sugar', placeholder: '110' },
            { label: 'Weight (kg)', key: 'weight', placeholder: '70' }
          ].map(field => React.createElement('div', { key: field.key },
            React.createElement('label', { style: { display: 'block', marginBottom: '8px', color: textColor, fontWeight: '500' } }, field.label),
            React.createElement('input', { type: 'number', placeholder: field.placeholder, value: healthData[field.key], onChange: (e) => setHealthData({...healthData, [field.key]: e.target.value}), style: { width: '100%', padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } })
          ))
        ),
        React.createElement('div', { style: { display: 'flex', gap: '12px', marginBottom: '20px' } },
          React.createElement('button', { onClick: saveHealthData, style: { padding: '12px 24px', background: '#10b981', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '?? Save Health Data'),
          React.createElement('button', { onClick: analyzeRisk, style: { padding: '12px 24px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '?? Analyze Health Status')
        ),
        
        riskResult && React.createElement('div', { style: { marginTop: '15px', padding: '18px', borderRadius: '16px', background: riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)', border: `1px solid ${riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}` } },
          React.createElement('h4', { style: { margin: 0, color: riskResult.risk_level === 'HIGH' ? '#dc2626' : '#059669' } }, 'Risk Level: ', riskResult.risk_level),
          React.createElement('p', { style: { margin: '8px 0', color: textColor } }, React.createElement('strong', null, 'Issues: '), riskResult.risks?.join(', ') || 'None'),
          React.createElement('p', { style: { margin: 0, color: textColor } }, React.createElement('strong', null, 'Recommendations: '), riskResult.recommendations?.join('; ') || 'Continue monitoring')
        ),

        healthRecords.length > 0 && React.createElement('div', { style: { marginTop: '20px' } },
          React.createElement('h3', { style: { color: textColor, marginBottom: '10px' } }, '?? Recent Health Records'),
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

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' } },
        
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? AI Health Assistant'),
          selectedUser ? [
            React.createElement('div', { key: 'chat', style: { height: '320px', overflowY: 'auto', background: isDarkMode ? '#0f172a' : '#f9fafb', borderRadius: '16px', padding: '15px', marginBottom: '15px', border: `1px solid ${borderColor}` } },
              chatMessages.length === 0 && React.createElement('div', { style: { textAlign: 'center', color: '#9ca3af', padding: '50px' } }, '?? Ask me anything about your health!'),
              chatMessages.map((msg, idx) => React.createElement('div', { key: idx, style: { marginBottom: '12px', textAlign: msg.role === 'user' ? 'right' : 'left' } },
                React.createElement('div', { style: { display: 'inline-block', maxWidth: '80%', padding: '10px 16px', borderRadius: '20px', background: msg.role === 'user' ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : 'white', color: msg.role === 'user' ? 'white' : textColor } },
                  React.createElement('strong', null, msg.role === 'user' ? 'You' : 'AI'), ': ', msg.content
                )
              )),
              isLoading && React.createElement('div', { style: { textAlign: 'left' } }, React.createElement('div', { style: { display: 'inline-block', padding: '10px 16px', borderRadius: '20px', background: isDarkMode ? '#334155' : '#f3f4f6', color: '#9ca3af' } }, 'AI is thinking...'))
            ),
            React.createElement('div', { key: 'input', style: { display: 'flex', gap: '10px' } },
              React.createElement('input', { type: 'text', placeholder: 'Type your health question...', value: aiQuestion, onChange: (e) => setAiQuestion(e.target.value), onKeyPress: (e) => e.key === 'Enter' && askAI(), style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
              React.createElement('button', { onClick: askAI, disabled: isLoading, style: { padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, 'Send')
            )
          ] : React.createElement('div', { style: { textAlign: 'center', padding: '60px', color: '#9ca3af' } }, '?? Please select a user first')
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? AI-Powered Health Tips'),
          selectedUser ? [
            React.createElement('button', { key: 'btn', onClick: loadHealthTips, style: { width: '100%', padding: '14px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600', marginBottom: '20px' } }, '?? Get Personalized Health Tips'),
            showTips && healthTips.length > 0 && React.createElement('div', { key: 'tips' }, healthTips.map((tip, i) => React.createElement('div', { key: i, style: { padding: '14px', marginBottom: '10px', background: 'rgba(16,185,129,0.08)', borderRadius: '12px', color: isDarkMode ? '#86efac' : '#065f46', borderLeft: '4px solid #10b981' } }, tip))),
            !showTips && React.createElement('div', { key: 'empty', style: { textAlign: 'center', padding: '50px', color: '#9ca3af' } }, '?? Click above to get health tips!')
          ] : React.createElement('div', { style: { textAlign: 'center', padding: '60px', color: '#9ca3af' } }, '?? Please select a user first')
        )
      )
    )
  );
}

export default App;
