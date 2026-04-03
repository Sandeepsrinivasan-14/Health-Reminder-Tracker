import React, { useState, useEffect } from 'react';

function App() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [healthData, setHealthData] = useState({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [riskResult, setRiskResult] = useState(null);

  useEffect(() => {
    fetchUsers();
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.style.background = '#0f172a';
    }
  }, []);

  const fetchUsers = async () => {
    const res = await fetch('https://health-reminder-tracker-api.onrender.com/users');
    const data = await res.json();
    setUsers(data);
  };

  const saveHealthData = async () => {
    if (!selectedUser) return;
    await fetch('https://health-reminder-tracker-api.onrender.com/health-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: selectedUser.id, ...healthData })
    });
    alert('Health data saved!');
  };

  const analyzeRisk = async () => {
    if (!selectedUser) return;
    const res = await fetch('https://health-reminder-tracker-api.onrender.com/api/ai/health-risk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ health_data: healthData })
    });
    const data = await res.json();
    setRiskResult(data);
  };

  const askAI = async () => {
    if (!aiQuestion.trim()) return;
    setChatMessages(prev => [...prev, { role: 'user', content: aiQuestion }]);
    setIsLoading(true);
    const res = await fetch('https://health-reminder-tracker-api.onrender.com/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: aiQuestion })
    });
    const data = await res.json();
    setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    setAiQuestion('');
    setIsLoading(false);
  };

  const loadHealthTips = async () => {
    const res = await fetch('https://health-reminder-tracker-api.onrender.com/health-tips');
    const data = await res.json();
    setHealthTips(data);
    setShowTips(true);
  };

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
    document.body.style.background = newTheme ? '#0f172a' : '#f0f2f5';
  };

  const cardBg = isDarkMode ? '#1e293b' : '#ffffff';
  const textColor = isDarkMode ? '#f1f5f9' : '#1f2937';

  return React.createElement('div', { style: { minHeight: '100vh', background: 'linear-gradient(135deg, #667eea, #764ba2)', padding: '20px' } },
    React.createElement('div', { style: { maxWidth: '1200px', margin: '0 auto' } },
      
      React.createElement('div', { style: { background: cardBg, borderRadius: '20px', padding: '20px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
        React.createElement('h1', { style: { color: textColor, margin: 0 } }, '🏥 Medical Health Tracker'),
        React.createElement('div', { style: { display: 'flex', gap: '10px', alignItems: 'center' } },
          React.createElement('button', { onClick: toggleTheme, style: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' } }, isDarkMode ? '☀️' : '🌙'),
          React.createElement('span', { style: { background: '#10b981', padding: '5px 12px', borderRadius: '20px', color: 'white', fontSize: '12px' } }, '✅ API: Healthy')
        )
      ),

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' } },
        React.createElement('div', { style: { background: cardBg, borderRadius: '20px', padding: '20px' } },
          React.createElement('h2', { style: { color: textColor } }, '👤 Users'),
          React.createElement('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '8px', maxHeight: '200px', overflowY: 'auto' } },
            users.map(user => React.createElement('button', { key: user.id, onClick: () => setSelectedUser(user), style: { padding: '8px 16px', background: selectedUser?.id === user.id ? '#667eea' : '#e5e7eb', color: selectedUser?.id === user.id ? 'white' : '#333', border: 'none', borderRadius: '20px', cursor: 'pointer' } }, user.name))
          ),
          selectedUser && React.createElement('p', { style: { marginTop: '10px', color: '#10b981' } }, '✅ Selected: ', selectedUser.name)
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '20px', padding: '20px', textAlign: 'center' } },
          React.createElement('h2', { style: { color: textColor } }, '🚨 Emergency SOS'),
          React.createElement('button', { onClick: async () => { await fetch('https://health-reminder-tracker-api.onrender.com/sos', { method: 'POST' }); alert('SOS Sent!'); }, style: { background: '#ef4444', color: 'white', padding: '15px 30px', border: 'none', borderRadius: '50px', fontSize: '18px', cursor: 'pointer' } }, '🚨 SOS EMERGENCY')
        )
      ),

      React.createElement('div', { style: { background: cardBg, borderRadius: '20px', padding: '20px', marginBottom: '20px' } },
        React.createElement('h2', { style: { color: textColor } }, '📊 Health Parameters'),
        React.createElement('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', marginBottom: '15px' } },
          ['bp_systolic', 'bp_diastolic', 'heart_rate', 'blood_sugar', 'weight'].map(f => 
            React.createElement('input', { key: f, type: 'number', placeholder: f, value: healthData[f], onChange: (e) => setHealthData({...healthData, [f]: e.target.value}), style: { padding: '10px', border: '1px solid #ddd', borderRadius: '8px', background: isDarkMode ? '#334155' : 'white', color: textColor } })
          )
        ),
        React.createElement('div', { style: { display: 'flex', gap: '10px' } },
          React.createElement('button', { onClick: saveHealthData, style: { padding: '10px 20px', background: '#10b981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' } }, '💾 Save'),
          React.createElement('button', { onClick: analyzeRisk, style: { padding: '10px 20px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' } }, '📊 Analyze Risk')
        ),
        riskResult && React.createElement('div', { style: { marginTop: '15px', padding: '15px', background: riskResult.risk_level === 'HIGH' ? '#fee2e2' : '#d1fae5', borderRadius: '8px' } },
          React.createElement('h4', { style: { margin: 0 } }, 'Risk Level: ', riskResult.risk_level),
          React.createElement('p', null, 'Issues: ', riskResult.risks?.join(', ') || 'None')
        )
      ),

      React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' } },
        React.createElement('div', { style: { background: cardBg, borderRadius: '20px', padding: '20px' } },
          React.createElement('h2', { style: { color: textColor } }, '🤖 AI Health Assistant'),
          React.createElement('div', { style: { height: '250px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '8px', padding: '10px', marginBottom: '10px', background: isDarkMode ? '#0f172a' : '#f9fafb' } },
            chatMessages.length === 0 && React.createElement('p', { style: { textAlign: 'center', color: '#999' } }, 'Ask me anything!'),
            chatMessages.map((msg, i) => React.createElement('div', { key: i, style: { textAlign: msg.role === 'user' ? 'right' : 'left', marginBottom: '8px' } },
              React.createElement('span', { style: { background: msg.role === 'user' ? '#667eea' : '#e5e7eb', padding: '8px 12px', borderRadius: '12px', color: msg.role === 'user' ? 'white' : '#333' } }, msg.content)
            )),
            isLoading && React.createElement('p', { style: { color: '#999' } }, 'AI is thinking...')
          ),
          React.createElement('div', { style: { display: 'flex', gap: '10px' } },
            React.createElement('input', { type: 'text', placeholder: 'Ask a health question...', value: aiQuestion, onChange: (e) => setAiQuestion(e.target.value), onKeyPress: (e) => e.key === 'Enter' && askAI(), style: { flex: 1, padding: '10px', border: '1px solid #ddd', borderRadius: '8px', background: isDarkMode ? '#334155' : 'white', color: textColor } }),
            React.createElement('button', { onClick: askAI, style: { padding: '10px 20px', background: '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' } }, 'Send')
          )
        ),

        React.createElement('div', { style: { background: cardBg, borderRadius: '20px', padding: '20px' } },
          React.createElement('h2', { style: { color: textColor } }, '💡 Health Tips'),
          React.createElement('button', { onClick: loadHealthTips, style: { padding: '10px 20px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', marginBottom: '15px' } }, '📋 Load Tips'),
          showTips && healthTips.map((tip, i) => React.createElement('div', { key: i, style: { padding: '10px', marginBottom: '8px', background: '#f3f4f6', borderRadius: '8px', color: '#333' } }, '✓ ', tip))
        )
      )
    )
  );
}

export default App;
