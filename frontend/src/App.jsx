import React, { useState } from 'react';

// HARDCODED USERS - Guaranteed to show immediately
const USERS = [
  { id: 1, name: "Test Patient" },
  { id: 2, name: "Rajesh Kumar" },
  { id: 3, name: "Priya Sharma" },
  { id: 4, name: "Amit Patel" },
  { id: 5, name: "Sunita Reddy" },
  { id: 6, name: "Vikram Singh" },
  { id: 7, name: "Neha Gupta" },
  { id: 8, name: "Anand Desai" },
  { id: 9, name: "Kavita Nair" },
  { id: 10, name: "Suresh Iyer" },
  { id: 11, name: "Meera Joshi" },
  { id: 12, name: "Rohan Mehta" },
  { id: 13, name: "Anjali Kulkarni" },
  { id: 14, name: "Deepak Saxena" },
  { id: 15, name: "Swati Choudhary" },
  { id: 16, name: "Manoj Verma" },
  { id: 17, name: "Pooja Malhotra" },
  { id: 18, name: "Arjun Nair" },
  { id: 19, name: "Divya Menon" },
  { id: 20, name: "Sanjay Gupta" },
  { id: 21, name: "Lata Mangeshkar" },
  { id: 22, name: "Lohith" }
];

function App() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [healthData, setHealthData] = useState({ bp_systolic: '', bp_diastolic: '', heart_rate: '', blood_sugar: '', weight: '' });
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [riskResult, setRiskResult] = useState(null);
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);

  const API_URL = 'https://health-reminder-tracker.onrender.com';

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
    
    setChatMessages(prev => [...prev, { role: 'user', content: aiQuestion }]);
    setIsLoading(true);
    
    const res = await fetch(`${API_URL}/api/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: aiQuestion, health_data: null, session_id: selectedUser.id.toString() })
    });
    const data = await res.json();
    setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    setAiQuestion('');
    setIsLoading(false);
  };

  const loadHealthTips = async () => {
    const res = await fetch(`${API_URL}/health-tips`);
    const data = await res.json();
    setHealthTips(data);
    setShowTips(true);
  };

  const sendSOS = async () => {
    await fetch(`${API_URL}/sos`, { method: 'POST' });
    alert('?? SOS Alert Sent!');
  };

  const exportPDF = () => {
    if (!selectedUser) return;
    window.open(`${API_URL}/export-pdf/${selectedUser.id}`, '_blank');
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'Arial', background: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)', borderRadius: '15px', padding: '20px', marginBottom: '20px', color: 'white' }}>
        <h1 style={{ margin: 0 }}>?? Medical Health Tracker</h1>
        <p>AI-Powered Healthcare Assistant</p>
        <div style={{ marginTop: '10px', background: 'rgba(255,255,255,0.2)', padding: '5px 10px', borderRadius: '10px', display: 'inline-block' }}>? API: Healthy</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        
        {/* User Selection - NOW WITH HARDCODED USERS */}
        <div style={{ background: 'white', borderRadius: '15px', padding: '20px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h2 style={{ margin: '0 0 15px', color: '#333' }}>?? Select Patient</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
            {USERS.map(user => (
              <button
                key={user.id}
                onClick={() => setSelectedUser(user)}
                style={{
                  padding: '8px 16px',
                  background: selectedUser?.id === user.id ? '#667eea' : '#e5e7eb',
                  color: selectedUser?.id === user.id ? 'white' : '#333',
                  border: 'none',
                  borderRadius: '20px',
                  cursor: 'pointer'
                }}
              >
                {user.name}
              </button>
            ))}
          </div>
          {selectedUser && <p style={{ marginTop: '10px', color: '#10b981' }}>? Selected: {selectedUser.name}</p>}
        </div>

        {/* SOS Card */}
        <div style={{ background: 'white', borderRadius: '15px', padding: '20px', textAlign: 'center', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h2 style={{ margin: '0 0 15px', color: '#333' }}>?? Emergency SOS</h2>
          <button onClick={sendSOS} style={{ background: '#ef4444', color: 'white', padding: '15px 30px', fontSize: '18px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: 'pointer' }}>?? SOS EMERGENCY</button>
          <button onClick={exportPDF} style={{ marginTop: '15px', padding: '10px 20px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', marginLeft: '10px' }}>?? Export PDF</button>
        </div>
      </div>

      {/* Health Parameters */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '20px', marginBottom: '20px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 15px', color: '#333' }}>?? Health Parameter Tracker</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '15px', marginBottom: '15px' }}>
          <input type="number" placeholder="BP Systolic" value={healthData.bp_systolic} onChange={(e) => setHealthData({...healthData, bp_systolic: e.target.value})} style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px' }} />
          <input type="number" placeholder="BP Diastolic" value={healthData.bp_diastolic} onChange={(e) => setHealthData({...healthData, bp_diastolic: e.target.value})} style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px' }} />
          <input type="number" placeholder="Heart Rate" value={healthData.heart_rate} onChange={(e) => setHealthData({...healthData, heart_rate: e.target.value})} style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px' }} />
          <input type="number" placeholder="Blood Sugar" value={healthData.blood_sugar} onChange={(e) => setHealthData({...healthData, blood_sugar: e.target.value})} style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px' }} />
          <input type="number" placeholder="Weight (kg)" value={healthData.weight} onChange={(e) => setHealthData({...healthData, weight: e.target.value})} style={{ padding: '10px', border: '1px solid #ddd', borderRadius: '8px' }} />
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={saveHealthData} style={{ padding: '10px 20px', background: '#10b981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>?? Save Health Data</button>
          <button onClick={analyzeRisk} style={{ padding: '10px 20px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>?? Analyze Health Status</button>
        </div>
        
        {riskResult && (
          <div style={{ marginTop: '15px', padding: '15px', background: riskResult.risk_level === 'HIGH' ? '#fee2e2' : '#d1fae5', borderRadius: '8px' }}>
            <h4>Risk Level: {riskResult.risk_level}</h4>
            <p><strong>Issues:</strong> {riskResult.risks?.join(', ') || 'None'}</p>
            <p><strong>Recommendations:</strong> {riskResult.recommendations?.join('; ') || 'Continue monitoring'}</p>
          </div>
        )}
      </div>

      {/* AI Chat */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '20px', marginBottom: '20px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 15px', color: '#333' }}>?? AI Health Assistant</h2>
        {selectedUser ? (
          <>
            <div style={{ height: '250px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '8px', padding: '10px', marginBottom: '10px', background: '#f9fafb' }}>
              {chatMessages.length === 0 && <p style={{ textAlign: 'center', color: '#999' }}>Ask me about {selectedUser.name}'s health!</p>}
              {chatMessages.map((msg, i) => (
                <div key={i} style={{ marginBottom: '8px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                  <span style={{ display: 'inline-block', padding: '8px 12px', borderRadius: '12px', background: msg.role === 'user' ? '#667eea' : '#e5e7eb', color: msg.role === 'user' ? 'white' : '#333' }}>
                    <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
                  </span>
                </div>
              ))}
              {isLoading && <p style={{ color: '#999' }}>AI is thinking...</p>}
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input type="text" placeholder="Ask about health..." value={aiQuestion} onChange={(e) => setAiQuestion(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && askAI()} style={{ flex: 1, padding: '10px', border: '1px solid #ddd', borderRadius: '8px' }} />
              <button onClick={askAI} disabled={isLoading} style={{ padding: '10px 20px', background: '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Send</button>
            </div>
          </>
        ) : <p style={{ textAlign: 'center', padding: '40px', color: '#999' }}>?? Please select a patient first</p>}
      </div>

      {/* Health Tips */}
      <div style={{ background: 'white', borderRadius: '15px', padding: '20px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 15px', color: '#333' }}>?? Health Tips</h2>
        <button onClick={loadHealthTips} style={{ padding: '10px 20px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>?? Load Health Tips</button>
        {showTips && healthTips.map((tip, i) => (
          <div key={i} style={{ padding: '10px', marginTop: '8px', background: '#f3f4f6', borderRadius: '8px' }}>? {tip}</div>
        ))}
      </div>
    </div>
  );
}

export default App;
