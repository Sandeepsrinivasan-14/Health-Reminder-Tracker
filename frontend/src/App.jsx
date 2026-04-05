import React, { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Health Data State
  const [healthData, setHealthData] = useState({
    bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: ''
  });
  const [healthRecords, setHealthRecords] = useState([]);
  const [riskResult, setRiskResult] = useState(null);
  
  // AI Chat State
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Tips State
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);
  
  // Notifications
  const [notifications, setNotifications] = useState([]);
  const [notificationCount, setNotificationCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  
  // New User
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');

  const API_URL = 'https://health-reminder-tracker.onrender.com';

  // Hardcoded fallback users
  const FALLBACK_USERS = [
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

  useEffect(() => {
    loadUsers();
    loadTips();
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') setDarkMode(true);
  }, []);

  useEffect(() => {
    if (selectedUser) {
      loadHealthRecords();
      loadNotifications();
    }
  }, [selectedUser]);

  const loadUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/users`);
      const data = await res.json();
      if (data && data.length > 0) {
        setUsers(data);
      } else {
        setUsers(FALLBACK_USERS);
      }
    } catch (err) {
      setUsers(FALLBACK_USERS);
    } finally {
      setLoading(false);
    }
  };

  const loadHealthRecords = async () => {
    try {
      const res = await fetch(`${API_URL}/health-data/user/${selectedUser.id}`);
      const data = await res.json();
      setHealthRecords(data);
      if (data && data.length > 0) {
        const latest = data[0];
        setHealthData({
          bp_systolic: latest.bp_systolic || '',
          bp_diastolic: latest.bp_diastolic || '',
          heart_rate: latest.heart_rate || '',
          blood_sugar: latest.blood_sugar || '',
          weight: latest.weight || ''
        });
      }
    } catch (err) {
      console.error("Failed to load records");
    }
  };

  const loadNotifications = async () => {
    try {
      const res = await fetch(`${API_URL}/api/notifications/alerts/${selectedUser.id}`);
      const data = await res.json();
      setNotifications(data);
      setNotificationCount(data.filter(n => !n.acknowledged).length);
    } catch (err) {}
  };

  const loadTips = async () => {
    try {
      const res = await fetch(`${API_URL}/health-tips`);
      const data = await res.json();
      setHealthTips(data);
    } catch (err) {
      setHealthTips([
        "Check blood pressure regularly",
        "Exercise 30 minutes daily",
        "Stay hydrated",
        "Get 7-8 hours of sleep",
        "Take medications on time"
      ]);
    }
  };

  const saveHealthData = async () => {
    if (!selectedUser) { alert('Select a patient first'); return; }
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
    loadHealthRecords();
  };

  const analyzeRisk = async () => {
    if (!selectedUser) { alert('Select a patient first'); return; }
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
    if (!selectedUser) { alert('Select a patient first'); return; }
    if (!chatInput.trim()) return;
    
    setChatMessages(prev => [...prev, { role: 'user', content: chatInput }]);
    setIsLoading(true);
    
    try {
      const res = await fetch(`${API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: chatInput, 
          health_data: healthData,
          session_id: selectedUser.id.toString() 
        })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, please try again.' }]);
    }
    setChatInput('');
    setIsLoading(false);
  };

  const sendSOS = async () => {
    try {
      await fetch(`${API_URL}/sos`, { method: 'POST' });
      alert('🚨 SOS Alert Sent! Caregiver notified.');
    } catch (err) {
      alert('⚠️ SOS would be sent here');
    }
  };

  const exportPDF = () => {
    if (!selectedUser) return;
    window.open(`${API_URL}/export-pdf/${selectedUser.id}`, '_blank');
  };

  const createUser = async () => {
    if (!newUserName || !newUserEmail) return;
    try {
      await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newUserName, email: newUserEmail })
      });
      setNewUserName('');
      setNewUserEmail('');
      loadUsers();
      alert('User created!');
    } catch (err) {
      alert('Error creating user');
    }
  };

  const acknowledgeNotification = async (id) => {
    await fetch(`${API_URL}/api/notifications/alerts/${id}/acknowledge`, { method: 'PUT' });
    loadNotifications();
  };

  const toggleTheme = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('darkMode', !darkMode);
  };

  const bgColor = darkMode ? '#1a1a2e' : '#f0f2f5';
  const cardBg = darkMode ? '#16213e' : '#ffffff';
  const textColor = darkMode ? '#e2e8f0' : '#1f2937';
  const borderColor = darkMode ? '#334155' : '#e5e7eb';

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)', padding: '20px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ background: cardBg, borderRadius: '20px', padding: '20px 30px', marginBottom: '25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '28px', color: textColor }}>🏥 Medical Health Tracker</h1>
            <p style={{ margin: '5px 0 0', color: textColor }}>AI-Powered Healthcare Assistant</p>
          </div>
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <button onClick={toggleTheme} style={{ background: 'rgba(0,0,0,0.1)', border: 'none', borderRadius: '50%', width: '40px', height: '40px', fontSize: '20px', cursor: 'pointer', color: textColor }}>{darkMode ? '☀️' : '🌙'}</button>
            <div style={{ background: '#10b981', padding: '6px 16px', borderRadius: '50px', color: 'white', fontSize: '13px', fontWeight: '600' }}>✅ API: Healthy</div>
            <div style={{ position: 'relative' }}>
              <button onClick={() => setShowNotifications(!showNotifications)} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', position: 'relative', color: textColor }}>
                🔔
                {notificationCount > 0 && <span style={{ position: 'absolute', top: '-5px', right: '-10px', background: '#ef4444', color: 'white', borderRadius: '50%', padding: '2px 6px', fontSize: '11px' }}>{notificationCount}</span>}
              </button>
              {showNotifications && (
                <div style={{ position: 'absolute', right: 0, top: '45px', width: '320px', background: 'white', borderRadius: '16px', boxShadow: '0 20px 40px rgba(0,0,0,0.15)', zIndex: 1000, maxHeight: '400px', overflow: 'auto' }}>
                  <div style={{ padding: '15px', borderBottom: '1px solid #e5e7eb', fontWeight: 'bold', color: '#1f2937' }}>🔔 Notifications</div>
                  {notifications.length === 0 ? <div style={{ padding: '30px', textAlign: 'center', color: '#9ca3af' }}>No notifications</div> :
                    notifications.map(n => (
                      <div key={n.id} style={{ padding: '12px 15px', borderBottom: '1px solid #f0f0f0' }}>
                        <div style={{ fontWeight: 'bold', color: n.level === 'danger' ? '#dc2626' : n.level === 'warning' ? '#f59e0b' : '#3b82f6' }}>{n.type}</div>
                        <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '4px' }}>{n.message}</div>
                        <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>{new Date(n.created_at).toLocaleString()}</div>
                        {!n.acknowledged && <button onClick={() => acknowledgeNotification(n.id)} style={{ marginTop: '8px', padding: '4px 12px', fontSize: '11px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '20px', cursor: 'pointer' }}>Mark Read</button>}
                      </div>
                    ))
                  }
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content - Two Columns */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' }}>
          
          {/* Left Column - Patient Selection & Health Data */}
          <div>
            {/* Patient Selection Card */}
            <div style={{ background: cardBg, borderRadius: '20px', padding: '25px', marginBottom: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
              <h2 style={{ color: textColor, marginBottom: '20px' }}>👤 Select Patient</h2>
              {loading ? (
                <p style={{ color: textColor }}>Loading patients...</p>
              ) : (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', maxHeight: '200px', overflowY: 'auto' }}>
                  {users.map(user => (
                    <button key={user.id} onClick={() => setSelectedUser(user)} style={{ padding: '8px 18px', background: selectedUser?.id === user.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : darkMode ? '#334155' : '#f3f4f6', color: selectedUser?.id === user.id ? 'white' : textColor, border: 'none', borderRadius: '50px', cursor: 'pointer', fontSize: '13px' }}>
                      {user.name}
                    </button>
                  ))}
                </div>
              )}
              {selectedUser && <p style={{ marginTop: '15px', padding: '10px', background: 'rgba(16,185,129,0.1)', borderRadius: '10px', color: '#10b981' }}>✅ Selected: {selectedUser.name}</p>}
            </div>

            {/* Create User Card */}
            <div style={{ background: cardBg, borderRadius: '20px', padding: '25px', marginBottom: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
              <h2 style={{ color: textColor, marginBottom: '20px' }}>➕ Create New Patient</h2>
              <div style={{ display: 'flex', gap: '12px' }}>
                <input type="text" placeholder="Full Name" value={newUserName} onChange={(e) => setNewUserName(e.target.value)} style={{ flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '10px', background: darkMode ? '#334155' : 'white', color: textColor }} />
                <input type="email" placeholder="Email" value={newUserEmail} onChange={(e) => setNewUserEmail(e.target.value)} style={{ flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '10px', background: darkMode ? '#334155' : 'white', color: textColor }} />
                <button onClick={createUser} style={{ padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer' }}>Create</button>
              </div>
            </div>

            {/* Health Parameters Card */}
            <div style={{ background: cardBg, borderRadius: '20px', padding: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
              <h2 style={{ color: textColor, marginBottom: '20px' }}>📊 Health Parameters</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px', marginBottom: '20px' }}>
                <div>
                  <label style={{ color: textColor, display: 'block', marginBottom: '5px' }}>BP Systolic (mmHg)</label>
                  <input type="number" value={healthData.bp_systolic} onChange={(e) => setHealthData({...healthData, bp_systolic: e.target.value})} style={{ width: '100%', padding: '10px', border: `1px solid ${borderColor}`, borderRadius: '8px', background: darkMode ? '#334155' : 'white', color: textColor }} placeholder="120" />
                </div>
                <div>
                  <label style={{ color: textColor, display: 'block', marginBottom: '5px' }}>BP Diastolic (mmHg)</label>
                  <input type="number" value={healthData.bp_diastolic} onChange={(e) => setHealthData({...healthData, bp_diastolic: e.target.value})} style={{ width: '100%', padding: '10px', border: `1px solid ${borderColor}`, borderRadius: '8px', background: darkMode ? '#334155' : 'white', color: textColor }} placeholder="80" />
                </div>
                <div>
                  <label style={{ color: textColor, display: 'block', marginBottom: '5px' }}>Heart Rate (BPM)</label>
                  <input type="number" value={healthData.heart_rate} onChange={(e) => setHealthData({...healthData, heart_rate: e.target.value})} style={{ width: '100%', padding: '10px', border: `1px solid ${borderColor}`, borderRadius: '8px', background: darkMode ? '#334155' : 'white', color: textColor }} placeholder="72" />
                </div>
                <div>
                  <label style={{ color: textColor, display: 'block', marginBottom: '5px' }}>Blood Sugar (mg/dL)</label>
                  <input type="number" value={healthData.blood_sugar} onChange={(e) => setHealthData({...healthData, blood_sugar: e.target.value})} style={{ width: '100%', padding: '10px', border: `1px solid ${borderColor}`, borderRadius: '8px', background: darkMode ? '#334155' : 'white', color: textColor }} placeholder="110" />
                </div>
                <div>
                  <label style={{ color: textColor, display: 'block', marginBottom: '5px' }}>Weight (kg)</label>
                  <input type="number" value={healthData.weight} onChange={(e) => setHealthData({...healthData, weight: e.target.value})} style={{ width: '100%', padding: '10px', border: `1px solid ${borderColor}`, borderRadius: '8px', background: darkMode ? '#334155' : 'white', color: textColor }} placeholder="70" />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button onClick={saveHealthData} style={{ padding: '12px 24px', background: '#10b981', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', flex: 1 }}>💾 Save Data</button>
                <button onClick={analyzeRisk} style={{ padding: '12px 24px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', flex: 1 }}>📊 Analyze Risk</button>
              </div>
              
              {riskResult && (
                <div style={{ marginTop: '20px', padding: '15px', background: riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)', borderRadius: '12px' }}>
                  <h4 style={{ margin: 0, color: riskResult.risk_level === 'HIGH' ? '#dc2626' : '#059669' }}>Risk Level: {riskResult.risk_level}</h4>
                  <p style={{ margin: '8px 0', color: textColor }}><strong>Issues:</strong> {riskResult.risks?.join(', ') || 'None'}</p>
                  <p style={{ margin: 0, color: textColor }}><strong>Recommendations:</strong> {riskResult.recommendations?.join('; ') || 'Continue monitoring'}</p>
                </div>
              )}

              {/* Health Records Table */}
              {healthRecords.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <h3 style={{ color: textColor, marginBottom: '10px' }}>📋 Recent Records</h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead><tr style={{ background: darkMode ? '#334155' : '#f3f4f6' }}>
                        <th style={{ padding: '8px', color: textColor }}>Date</th><th style={{ padding: '8px', color: textColor }}>BP</th><th style={{ padding: '8px', color: textColor }}>HR</th><th style={{ padding: '8px', color: textColor }}>Sugar</th><th style={{ padding: '8px', color: textColor }}>Weight</th>
                      </tr></thead>
                      <tbody>
                        {healthRecords.slice(0, 5).map((r, i) => (
                          <tr key={i} style={{ borderBottom: `1px solid ${borderColor}` }}>
                            <td style={{ padding: '6px', color: textColor }}>{new Date(r.recorded_at).toLocaleDateString()}</td>
                            <td style={{ padding: '6px', color: textColor }}>{r.bp_systolic}/{r.bp_diastolic}</td>
                            <td style={{ padding: '6px', color: textColor }}>{r.heart_rate}</td>
                            <td style={{ padding: '6px', color: textColor }}>{r.blood_sugar}</td>
                            <td style={{ padding: '6px', color: textColor }}>{r.weight}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - SOS, AI Chat & Tips */}
          <div>
            {/* SOS & Reports Card */}
            <div style={{ background: cardBg, borderRadius: '20px', padding: '25px', marginBottom: '25px', textAlign: 'center', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
              <h2 style={{ color: textColor, marginBottom: '20px' }}>🚨 Emergency SOS</h2>
              <button onClick={sendSOS} style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', padding: '15px 40px', fontSize: '18px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 20px rgba(239,68,68,0.3)' }}>🚨 SOS EMERGENCY</button>
              <button onClick={exportPDF} style={{ marginTop: '15px', padding: '10px 24px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', marginLeft: '10px' }}>📄 Export PDF</button>
            </div>

            {/* AI Chat Card */}
            <div style={{ background: cardBg, borderRadius: '20px', padding: '25px', marginBottom: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
              <h2 style={{ color: textColor, marginBottom: '20px' }}>🤖 AI Health Assistant</h2>
              {selectedUser ? (
                <>
                  <div style={{ height: '300px', overflowY: 'auto', background: darkMode ? '#0f172a' : '#f9fafb', borderRadius: '12px', padding: '15px', marginBottom: '15px', border: `1px solid ${borderColor}` }}>
                    {chatMessages.length === 0 && <p style={{ textAlign: 'center', color: '#9ca3af', padding: '40px' }}>💬 Ask me about {selectedUser.name}'s health!</p>}
                    {chatMessages.map((msg, i) => (
                      <div key={i} style={{ marginBottom: '10px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                        <span style={{ display: 'inline-block', padding: '8px 14px', borderRadius: '18px', background: msg.role === 'user' ? 'linear-gradient(135deg, #667eea, #764ba2)' : darkMode ? '#334155' : '#e5e7eb', color: msg.role === 'user' ? 'white' : textColor }}>
                          <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
                        </span>
                      </div>
                    ))}
                    {isLoading && <p style={{ color: '#9ca3af' }}>AI is thinking...</p>}
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <input type="text" placeholder="Ask about health..." value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && askAI()} style={{ flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '10px', background: darkMode ? '#334155' : 'white', color: textColor }} />
                    <button onClick={askAI} disabled={isLoading} style={{ padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer' }}>Send</button>
                  </div>
                </>
              ) : <p style={{ textAlign: 'center', padding: '50px', color: '#9ca3af' }}>👤 Please select a patient first</p>}
            </div>

            {/* Health Tips Card */}
            <div style={{ background: cardBg, borderRadius: '20px', padding: '25px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
              <h2 style={{ color: textColor, marginBottom: '20px' }}>💡 Health Tips</h2>
              <button onClick={() => setShowTips(!showTips)} style={{ padding: '12px 24px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', marginBottom: '15px' }}>{showTips ? 'Hide Tips' : '📋 Show Health Tips'}</button>
              {showTips && healthTips.map((tip, i) => (
                <div key={i} style={{ padding: '10px', marginBottom: '8px', background: 'rgba(16,185,129,0.08)', borderRadius: '8px', color: textColor, borderLeft: '4px solid #10b981' }}>✓ {tip}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
