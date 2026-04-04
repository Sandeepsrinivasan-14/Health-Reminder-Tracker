import React, { useState, useEffect } from 'react';

function App() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [healthData, setHealthData] = useState({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);
  const [isLoadingTips, setIsLoadingTips] = useState(false);
  const [detectedConditions, setDetectedConditions] = useState([]);
  const [riskResult, setRiskResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [healthRecords, setHealthRecords] = useState([]);

  const API_URL = 'https://health-reminder-tracker.onrender.com';

  useEffect(() => {
    fetchUsers();
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.style.background = '#0f172a';
    }
  }, []);

  useEffect(() => {
    if (selectedUser) {
      fetchHealthRecords();
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [selectedUser]);

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/users`);
      const data = await res.json();
      setUsers(data);
    } catch (err) {
      console.error('Failed to fetch users');
    }
  };

  const fetchHealthRecords = async () => {
    if (!selectedUser) return;
    try {
      const res = await fetch(`${API_URL}/health-data/user/${selectedUser.id}`);
      const data = await res.json();
      setHealthRecords(data);
    } catch (err) {
      console.error('Failed to fetch health records');
    }
  };

  const fetchNotifications = async () => {
    if (!selectedUser) return;
    try {
      const res = await fetch(`${API_URL}/api/notifications/alerts/${selectedUser.id}`);
      const data = await res.json();
      setNotifications(data);
      setNotificationCount(data.filter(a => !a.acknowledged).length);
    } catch (err) {}
  };

  const createUser = async () => {
    if (!newUserName || !newUserEmail) return;
    await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newUserName, email: newUserEmail })
    });
    setNewUserName('');
    setNewUserEmail('');
    fetchUsers();
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
    if (!selectedUser) { alert('Please select a user first'); return; }
    setIsLoadingTips(true);
    try {
      const requestBody = {
        user_id: selectedUser.id,
        user_name: selectedUser.name,
        health_data: healthRecords.length > 0 ? {
          bp_systolic: healthRecords[0].bp_systolic || 120,
          bp_diastolic: healthRecords[0].bp_diastolic || 80,
          heart_rate: healthRecords[0].heart_rate || 75,
          blood_sugar: healthRecords[0].blood_sugar || 100,
          weight: healthRecords[0].weight || 70
        } : {}
      };
      
      const response = await fetch(`${API_URL}/api/ai/health-tips`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      const data = await response.json();
      setHealthTips(data.tips || ['Unable to generate tips']);
      setDetectedConditions(data.conditions || []);
      setShowTips(true);
    } catch (error) {
      setHealthTips(['Unable to load personalized tips. Please try again.']);
      setShowTips(true);
    } finally {
      setIsLoadingTips(false);
    }
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

  const acknowledgeAlert = async (alertId) => {
    await fetch(`${API_URL}/api/notifications/alerts/${alertId}/acknowledge`, { method: 'PUT' });
    fetchNotifications();
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
      
      // Header
      React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '20px 30px', marginBottom: '25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
        React.createElement('div', null,
          React.createElement('h1', { style: { margin: 0, fontSize: '28px', color: textColor } }, '?? Medical Health Tracker'),
          React.createElement('p', { style: { margin: '5px 0 0', color: textColor } }, 'AI-Powered Healthcare Assistant')
        ),
        React.createElement('div', { style: { display: 'flex', gap: '15px', alignItems: 'center' } },
          React.createElement('button', { onClick: toggleTheme, style: { background: 'rgba(0,0,0,0.1)', border: 'none', borderRadius: '50%', width: '40px', height: '40px', fontSize: '20px', cursor: 'pointer', color: textColor } }, isDarkMode ? '??' : '??'),
          React.createElement('div', { style: { background: '#10b981', padding: '6px 16px', borderRadius: '50px', color: 'white', fontSize: '13px', fontWeight: '600' } }, '? API: Healthy'),
          React.createElement('div', { style: { position: 'relative' } },
            React.createElement('button', { onClick: () => setShowNotifications(!showNotifications), style: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', position: 'relative', color: textColor } }, '??', notificationCount > 0 && React.createElement('span', { style: { position: 'absolute', top: '-5px', right: '-10px', background: '#ef4444', color: 'white', borderRadius: '50%', padding: '2px 6px', fontSize: '11px' } }, notificationCount)),
            showNotifications && React.createElement('div', { style: { position: 'absolute', right: 0, top: '45px', width: '320px', background: 'white', borderRadius: '16px', boxShadow: '0 20px 40px rgba(0,0,0,0.15)', zIndex: 1000, maxHeight: '400px', overflow: 'auto' } },
              React.createElement('div', { style: { padding: '15px', borderBottom: '1px solid #e5e7eb', fontWeight: 'bold', color: '#1f2937' } }, '?? Notifications'),
              notifications.length === 0 ? React.createElement('div', { style: { padding: '30px', textAlign: 'center', color: '#9ca3af' } }, 'No notifications') :
                notifications.map(n => React.createElement('div', { key: n.id, style: { padding: '12px 15px', borderBottom: '1px solid #f0f0f0' } },
                  React.createElement('div', { style: { fontWeight: 'bold', color: n.level === 'danger' ? '#dc2626' : n.level === 'warning' ? '#f59e0b' : '#3b82f6' } }, n.type),
                  React.createElement('div', { style: { fontSize: '13px', color: '#6b7280', marginTop: '4px' } }, n.message),
                  !n.acknowledged && React.createElement('button', { onClick: () => acknowledgeAlert(n.id), style: { marginTop: '8px', padding: '4px 12px', fontSize: '11px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '20px', cursor: 'pointer' } }, 'Mark Read')
                ))
            )
          )
        )
      ),

      // Row 1 - Create User + SOS
      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' } },
        
        // Create User Card
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? Create User'),
          React.createElement('div', { style: { display: 'flex', gap: '12px', marginBottom: '20px' } },
            React.createElement('input', { type: 'text', placeholder: 'Full Name', value: newUserName, onChange: (e) => setNewUserName(e.target.value), style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
            React.createElement('input', { type: 'email', placeholder: 'Email', value: newUserEmail, onChange: (e) => setNewUserEmail(e.target.value), style: { flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: inputBg, color: textColor } }),
            React.createElement('button', { onClick: createUser, style: { padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, 'Create')
          ),
          React.createElement('h3', { style: { color: textColor, fontSize: '16px', marginBottom: '12px' } }, `?? Existing Users (${users.length})`),
          React.createElement('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '10px', maxHeight: '200px', overflowY: 'auto' } },
            users.map(user => React.createElement('button', { key: user.id, onClick: () => setSelectedUser(user), style: { padding: '8px 18px', background: selectedUser?.id === user.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : '#f3f4f6', color: selectedUser?.id === user.id ? 'white' : textColor, border: 'none', borderRadius: '50px', cursor: 'pointer', fontSize: '13px' } }, user.name))
          ),
          selectedUser && React.createElement('div', { style: { marginTop: '15px', padding: '12px', background: 'rgba(16,185,129,0.1)', borderRadius: '12px' } }, React.createElement('span', { style: { color: '#059669', fontWeight: '600' } }, '? Selected: ', selectedUser.name))
        ),

        // SOS Card
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', textAlign: 'center' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? Emergency SOS'),
          React.createElement('button', { onClick: sendSOS, style: { background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', padding: '16px 40px', fontSize: '18px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(239,68,68,0.3)' } }, '?? SOS EMERGENCY'),
          React.createElement('button', { onClick: exportPDF, style: { marginTop: '15px', padding: '10px 20px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' } }, '?? Export PDF Report')
        )
      ),

      // Health Parameter Tracker
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

        // Health Records Table
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

      // Bottom Row - AI Chat + Health Tips
      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' } },
        
        // AI Chat
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

        // AI Health Tips
        React.createElement('div', { style: { background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' } },
          React.createElement('h2', { style: { color: textColor, marginBottom: '20px' } }, '?? AI-Powered Health Tips'),
          selectedUser ? [
            React.createElement('button', { key: 'btn', onClick: loadHealthTips, disabled: isLoadingTips, style: { width: '100%', padding: '14px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', color: 'white', border: 'none', borderRadius: '12px', cursor: isLoadingTips ? 'not-allowed' : 'pointer', fontWeight: '600', marginBottom: '20px' } }, isLoadingTips ? '?? Generating AI Tips...' : '?? Get Personalized AI Tips'),
            detectedConditions.length > 0 && React.createElement('div', { key: 'conditions', style: { marginBottom: '20px', padding: '12px', background: 'rgba(245,158,11,0.1)', borderRadius: '12px' } }, React.createElement('strong', { style: { color: '#d97706' } }, '?? Detected: '), React.createElement('span', { style: { color: isDarkMode ? '#fcd34d' : '#92400e' } }, detectedConditions.join(', '))),
            showTips && healthTips.length > 0 && React.createElement('div', { key: 'tips' }, healthTips.map((tip, i) => React.createElement('div', { key: i, style: { padding: '14px', marginBottom: '10px', background: 'rgba(16,185,129,0.08)', borderRadius: '12px', color: isDarkMode ? '#86efac' : '#065f46', borderLeft: '4px solid #10b981' } }, tip))),
            !showTips && React.createElement('div', { key: 'empty', style: { textAlign: 'center', padding: '50px', color: '#9ca3af' } }, '?? Click above to get AI-generated health tips!')
          ] : React.createElement('div', { style: { textAlign: 'center', padding: '60px', color: '#9ca3af' } }, '?? Please select a user first')
        )
      )
    )
  );
}

export default App;
