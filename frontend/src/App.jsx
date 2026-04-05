import React, { useState, useEffect } from 'react';

// Complete Health Records Component
const HealthRecords = ({ userId, isDarkMode }) => {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    if (userId) {
      fetch(`https://health-reminder-tracker.onrender.com/health-data/user/${userId}`)
        .then(res => res.json())
        .then(setRecords);
    }
  }, [userId]);

  if (!records.length) return null;

  const textColor = isDarkMode ? '#e2e8f0' : '#1f2937';
  const borderColor = isDarkMode ? '#334155' : '#e5e7eb';

  return React.createElement('div', { style: { marginTop: '20px' } },
    React.createElement('h3', { style: { color: textColor, marginBottom: '15px' } }, '📋 Recent Health Records'),
    React.createElement('div', { style: { overflowX: 'auto' } },
      React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
        React.createElement('thead', null,
          React.createElement('tr', { style: { background: isDarkMode ? '#334155' : '#f3f4f6' } },
            ['Date', 'BP', 'HR', 'Sugar', 'Weight'].map(h => React.createElement('th', { key: h, style: { padding: '10px', textAlign: 'left', color: textColor } }, h))
          )
        ),
        React.createElement('tbody', null,
          records.slice(0, 5).map((r, i) => React.createElement('tr', { key: i, style: { borderBottom: `1px solid ${borderColor}` } },
            React.createElement('td', { style: { padding: '8px', color: textColor } }, new Date(r.recorded_at).toLocaleDateString()),
            React.createElement('td', { style: { padding: '8px', color: textColor } }, `${r.bp_systolic}/${r.bp_diastolic}`),
            React.createElement('td', { style: { padding: '8px', color: textColor } }, r.heart_rate),
            React.createElement('td', { style: { padding: '8px', color: textColor } }, r.blood_sugar),
            React.createElement('td', { style: { padding: '8px', color: textColor } }, r.weight)
          ))
        )
      )
    )
  );
};

// SOS Button Component
const SOSButton = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const sendSOS = async () => {
    setLoading(true);
    try {
      const res = await fetch('https://health-reminder-tracker.onrender.com/sos', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'sent') {
        setMessage('✅ SOS Alert Sent! Caregiver notified.');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (err) {
      setMessage('❌ Failed to send SOS');
    } finally {
      setLoading(false);
    }
  };

  return React.createElement('div', { style: { textAlign: 'center' } },
    React.createElement('button', {
      onClick: sendSOS,
      disabled: loading,
      style: {
        background: 'linear-gradient(135deg, #ef4444, #dc2626)',
        color: 'white',
        padding: '16px 40px',
        fontSize: '18px',
        fontWeight: 'bold',
        border: 'none',
        borderRadius: '50px',
        cursor: loading ? 'not-allowed' : 'pointer',
        boxShadow: '0 10px 30px rgba(239,68,68,0.3)',
        transition: 'transform 0.2s'
      }
    }, loading ? '📡 Sending...' : '🚨 SOS EMERGENCY'),
    message && React.createElement('div', { style: { marginTop: '10px', color: '#22c55e' } }, message)
  );
};

// Create User Component
const CreateUser = ({ onUserCreated }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const createUser = async () => {
    if (!name || !email) return;
    await fetch('https://health-reminder-tracker.onrender.com/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email })
    });
    setName('');
    setEmail('');
    onUserCreated();
  };

  return React.createElement('div', null,
    React.createElement('div', { style: { display: 'flex', gap: '12px', marginBottom: '20px' } },
      React.createElement('input', { type: 'text', placeholder: 'Full Name', value: name, onChange: (e) => setName(e.target.value), style: { flex: 1, padding: '12px', border: '1px solid #ddd', borderRadius: '12px' } }),
      React.createElement('input', { type: 'email', placeholder: 'Email', value: email, onChange: (e) => setEmail(e.target.value), style: { flex: 1, padding: '12px', border: '1px solid #ddd', borderRadius: '12px' } }),
      React.createElement('button', { onClick: createUser, style: { padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, 'Create')
    )
  );
};

// Health Tips Component
const HealthTips = () => {
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadTips = async () => {
    setLoading(true);
    const res = await fetch('https://health-reminder-tracker.onrender.com/health-tips');
    const data = await res.json();
    setTips(data);
    setLoading(false);
  };

  return React.createElement('div', null,
    React.createElement('button', { onClick: loadTips, style: { padding: '10px 20px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', marginBottom: '15px' } }, loading ? 'Loading...' : '📋 Load Health Tips'),
    tips.length > 0 && React.createElement('div', { style: { marginTop: '15px' } }, tips.map((tip, i) => React.createElement('div', { key: i, style: { padding: '10px', marginBottom: '8px', background: '#f3f4f6', borderRadius: '8px', color: '#333' } }, '✓ ', tip)))
  );
};

// Notification Bell Component
const NotificationBell = ({ userId }) => {
  const [notifications, setNotifications] = useState([]);
  const [show, setShow] = useState(false);
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (userId) {
      fetch(`https://health-reminder-tracker.onrender.com/api/notifications/alerts/${userId}`)
        .then(res => res.json())
        .then(data => {
          setNotifications(data);
          setCount(data.filter(n => !n.acknowledged).length);
        });
    }
  }, [userId]);

  const acknowledge = async (id) => {
    await fetch(`https://health-reminder-tracker.onrender.com/api/notifications/alerts/${id}/acknowledge`, { method: 'PUT' });
    setNotifications(notifications.map(n => n.id === id ? { ...n, acknowledged: true } : n));
    setCount(count - 1);
  };

  return React.createElement('div', { style: { position: 'relative' } },
    React.createElement('button', { onClick: () => setShow(!show), style: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', position: 'relative' } }, '🔔', count > 0 && React.createElement('span', { style: { position: 'absolute', top: '-5px', right: '-10px', background: '#ef4444', color: 'white', borderRadius: '50%', padding: '2px 6px', fontSize: '11px' } }, count)),
    show && React.createElement('div', { style: { position: 'absolute', right: 0, top: '45px', width: '320px', background: 'white', borderRadius: '16px', boxShadow: '0 20px 40px rgba(0,0,0,0.15)', zIndex: 1000, maxHeight: '400px', overflow: 'auto' } },
      React.createElement('div', { style: { padding: '15px', borderBottom: '1px solid #e5e7eb', fontWeight: 'bold', color: '#1f2937' } }, '🔔 Notifications'),
      notifications.length === 0 ? React.createElement('div', { style: { padding: '30px', textAlign: 'center', color: '#9ca3af' } }, 'No notifications') :
        notifications.map(n => React.createElement('div', { key: n.id, style: { padding: '12px 15px', borderBottom: '1px solid #f0f0f0' } },
          React.createElement('div', { style: { fontWeight: 'bold', color: n.level === 'danger' ? '#dc2626' : n.level === 'warning' ? '#f59e0b' : '#3b82f6' } }, n.type),
          React.createElement('div', { style: { fontSize: '13px', color: '#6b7280', marginTop: '4px' } }, n.message),
          !n.acknowledged && React.createElement('button', { onClick: () => acknowledge(n.id), style: { marginTop: '8px', padding: '4px 12px', fontSize: '11px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '20px', cursor: 'pointer' } }, 'Mark Read')
        ))
    )
  );
};

// Main App
function App() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [healthData, setHealthData] = useState({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
  const [riskResult, setRiskResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showTips, setShowTips] = useState(false);

  const API_URL = 'https://health-reminder-tracker.onrender.com';

  useEffect(() => {
    fetchUsers();
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.style.background = '#0f172a';
    }
  }, []);

  const fetchUsers = async () => {
    const res = await fetch(`${API_URL}/users`);
    const data = await res.json();
    setUsers(data);
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

  const loadHealthTips = () => {
    setShowTips(true);
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
          React.createElement('div', { style: { background: '#10b981', padding: '6px 16px', borderRadius: '50px', color: 'white', fontSize: '13px', fontWeight: '600' } }, '✅ API: Healthy'),
          selectedUser && React.createElement(NotificationBell, { userId: selectedUser.id })
        )
      ),

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' } },
        
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '👤 Create User'),
          React.createElement(CreateUser, { onUserCreated: fetchUsers }),
          React.createElement('h3', { style: { color: textColor, fontSize: '16px', marginBottom: '12px' } }, `📋 Existing Users (${users.length})`),
          React.createElement('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '10px', maxHeight: '250px', overflowY: 'auto' } },
            users.map(user => React.createElement('button', { key: user.id, onClick: () => setSelectedUser(user), style: { padding: '8px 18px', background: selectedUser?.id === user.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : '#f3f4f6', color: selectedUser?.id === user.id ? 'white' : textColor, border: 'none', borderRadius: '50px', cursor: 'pointer', fontSize: '13px', margin: '4px' } }, user.name))
          ),
          selectedUser && React.createElement('div', { style: { marginTop: '15px', padding: '12px', background: 'rgba(16,185,129,0.1)', borderRadius: '12px' } }, React.createElement('span', { style: { color: '#059669', fontWeight: '600' } }, '✅ Selected: ', selectedUser.name))
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', textAlign: 'center' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '🚨 Emergency SOS'),
          React.createElement(SOSButton, null),
          React.createElement('button', { onClick: exportPDF, style: { marginTop: '15px', padding: '10px 20px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '📄 Export PDF Report')
        )
      ),

      React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', marginBottom: '25px' } },
        React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '📊 Health Parameter Tracker'),
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
          React.createElement('button', { onClick: saveHealthData, style: { padding: '12px 24px', background: '#10b981', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '💾 Save Health Data'),
          React.createElement('button', { onClick: analyzeRisk, style: { padding: '12px 24px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '📊 Analyze Health Status')
        ),
        
        riskResult && React.createElement('div', { style: { marginTop: '15px', padding: '18px', borderRadius: '16px', background: riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)', border: `1px solid ${riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}` } },
          React.createElement('h4', { style: { margin: 0, color: riskResult.risk_level === 'HIGH' ? '#dc2626' : '#059669' } }, 'Risk Level: ', riskResult.risk_level),
          React.createElement('p', { style: { margin: '8px 0', color: textColor } }, React.createElement('strong', null, 'Issues: '), riskResult.risks?.join(', ') || 'None'),
          React.createElement('p', { style: { margin: 0, color: textColor } }, React.createElement('strong', null, 'Recommendations: '), riskResult.recommendations?.join('; ') || 'Continue monitoring')
        ),
        
        selectedUser && React.createElement(HealthRecords, { userId: selectedUser.id, isDarkMode: isDarkMode })
      ),

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' } },
        
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '🤖 AI Health Assistant'),
          selectedUser ? [
            React.createElement('div', { key: 'chat', style: { height: '320px', overflowY: 'auto', background: isDarkMode ? '#0f172a' : '#f9fafb', borderRadius: '16px', padding: '15px', marginBottom: '15px', border: `1px solid ${borderColor}` } },
              chatMessages.length === 0 && React.createElement('div', { style: { textAlign: 'center', color: '#9ca3af', padding: '50px' } }, '💬 Ask me anything about your health!'),
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
          ] : React.createElement('div', { style: { textAlign: 'center', padding: '60px', color: '#9ca3af' } }, '👤 Please select a user first')
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '💡 Health Tips'),
          React.createElement(HealthTips, null),
          showTips && React.createElement('div', { style: { marginTop: '15px', padding: '15px', background: '#f3f4f6', borderRadius: '8px' } },
            React.createElement('p', { style: { color: '#333' } }, '✓ Check your blood sugar regularly and take medicines on time'),
            React.createElement('p', { style: { color: '#333' } }, '✓ Walk at least 30 minutes a day, 5 days a week'),
            React.createElement('p', { style: { color: '#333' } }, '✓ Drink enough water and include fruits/vegetables in every meal'),
            React.createElement('p', { style: { color: '#333' } }, '✓ Take medication at the same time each day for better adherence'),
            React.createElement('p', { style: { color: '#333' } }, '✓ Get 7-8 hours of sleep for better immunity'),
            React.createElement('p', { style: { color: '#333' } }, '✓ Regular exercise helps manage chronic conditions')
          )
        )
      )
    )
  );
}

export default App;
