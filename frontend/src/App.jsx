import React, { useState, useEffect } from 'react';

const USERS = [
  { id: 1, name: "Test Patient", condition: "Healthy", bp: "118/78", hr: 72, sugar: 95, weight: 68 },
  { id: 2, name: "Rajesh Kumar", condition: "Diabetes", bp: "135/85", hr: 78, sugar: 180, weight: 75 },
  { id: 3, name: "Priya Sharma", condition: "Healthy", bp: "118/78", hr: 72, sugar: 95, weight: 68 },
  { id: 4, name: "Amit Patel", condition: "Heart Disease", bp: "145/90", hr: 95, sugar: 115, weight: 78 },
  { id: 5, name: "Sunita Reddy", condition: "Hypertension", bp: "155/95", hr: 82, sugar: 110, weight: 80 },
  { id: 6, name: "Vikram Singh", condition: "Diabetes", bp: "135/85", hr: 78, sugar: 180, weight: 75 },
  { id: 7, name: "Neha Gupta", condition: "Asthma", bp: "120/78", hr: 75, sugar: 95, weight: 65 },
  { id: 8, name: "Anand Desai", condition: "Hypertension", bp: "155/95", hr: 82, sugar: 110, weight: 80 },
  { id: 9, name: "Kavita Nair", condition: "Thyroid", bp: "125/80", hr: 70, sugar: 100, weight: 85 },
  { id: 10, name: "Suresh Iyer", condition: "Heart Disease", bp: "145/90", hr: 95, sugar: 115, weight: 78 },
  { id: 11, name: "Meera Joshi", condition: "Migraine", bp: "118/75", hr: 68, sugar: 92, weight: 62 },
  { id: 12, name: "Rohan Mehta", condition: "Healthy", bp: "118/78", hr: 72, sugar: 95, weight: 68 },
  { id: 13, name: "Anjali Kulkarni", condition: "Diabetes", bp: "135/85", hr: 78, sugar: 180, weight: 75 },
  { id: 14, name: "Deepak Saxena", condition: "Obesity", bp: "140/88", hr: 85, sugar: 125, weight: 110 },
  { id: 15, name: "Swati Choudhary", condition: "Anemia", bp: "105/65", hr: 88, sugar: 85, weight: 55 },
  { id: 16, name: "Manoj Verma", condition: "Hypertension", bp: "155/95", hr: 82, sugar: 110, weight: 80 },
  { id: 17, name: "Pooja Malhotra", condition: "Osteoporosis", bp: "130/82", hr: 72, sugar: 100, weight: 60 },
  { id: 18, name: "Arjun Nair", condition: "Healthy", bp: "118/78", hr: 72, sugar: 95, weight: 68 },
  { id: 19, name: "Divya Menon", condition: "PCOS", bp: "128/82", hr: 76, sugar: 115, weight: 82 },
  { id: 20, name: "Sanjay Gupta", condition: "Diabetes", bp: "135/85", hr: 78, sugar: 180, weight: 75 },
  { id: 21, name: "Lata Mangeshkar", condition: "Hypertension", bp: "155/95", hr: 82, sugar: 110, weight: 80 },
  { id: 22, name: "Lohith", condition: "Healthy", bp: "118/78", hr: 72, sugar: 95, weight: 68 }
];

function App() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [riskResult, setRiskResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [healthTips, setHealthTips] = useState([]);
  const [showTips, setShowTips] = useState(false);

  const API_URL = 'https://health-reminder-tracker.onrender.com';

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.style.background = '#0f172a';
    }
  }, []);

  const analyzeRisk = async () => {
    if (!selectedUser) return;
    const bpParts = selectedUser.bp.split('/');
    const riskBody = {
      health_data: {
        bp_systolic: parseInt(bpParts[0]),
        bp_diastolic: parseInt(bpParts[1]),
        heart_rate: selectedUser.hr,
        blood_sugar: selectedUser.sugar,
        weight: selectedUser.weight
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
    if (!selectedUser) return;
    if (!aiQuestion.trim()) return;
    
    const userMessage = aiQuestion;
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setAiQuestion('');
    setIsLoading(true);
    
    const bpParts = selectedUser.bp.split('/');
    const healthData = {
      bp_systolic: parseInt(bpParts[0]),
      bp_diastolic: parseInt(bpParts[1]),
      heart_rate: selectedUser.hr,
      blood_sugar: selectedUser.sugar,
      weight: selectedUser.weight
    };
    
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
    const tips = {
      "Diabetes": ["🩸 Monitor blood sugar daily", "🥗 Eat low glycemic index foods", "🚶 Walk after meals", "💊 Take insulin on time"],
      "Hypertension": ["❤️ Reduce salt intake", "🚶 Walk 30 mins daily", "💧 Drink more water", "🥦 Eat more potassium"],
      "Heart Disease": ["💔 Take aspirin as prescribed", "🚶 Light exercise only", "🥗 Low fat diet", "💊 Take medications on time"],
      "Healthy": ["✅ Keep up the good work!", "🥗 Eat balanced diet", "🚶 Stay active", "💧 Stay hydrated"],
      "Asthma": ["🌬️ Use inhaler as prescribed", "🚶 Avoid triggers", "💨 Practice breathing exercises"],
      "Thyroid": ["🦋 Take thyroid medication daily", "🥗 Eat iodine-rich foods", "💊 Don't skip doses"],
      "Obesity": ["⚖️ Track your calories", "🚶 Walk 10k steps daily", "🥗 Eat more protein", "💧 Drink water before meals"],
      "Anemia": ["🩸 Eat iron-rich foods", "🥩 Include red meat", "🥬 Eat spinach", "💊 Take iron supplements"],
      "PCOS": ["🌸 Maintain healthy weight", "🥗 Low carb diet", "🚶 Regular exercise", "💊 Take prescribed meds"],
      "Migraine": ["🧠 Avoid triggers", "💧 Stay hydrated", "😴 Regular sleep schedule", "☕ Limit caffeine"],
      "Osteoporosis": ["🦴 Increase calcium intake", "☀️ Get Vitamin D", "🏋️ Weight bearing exercises"]
    };
    setHealthTips(tips[selectedUser.condition] || tips["Healthy"]);
    setShowTips(true);
  };

  const sendSOS = async () => {
    try {
      await fetch(`${API_URL}/sos`, { method: 'POST' });
      alert('🚨 SOS Alert Sent!');
    } catch (err) {
      alert('❌ Failed to send SOS');
    }
  };

  const exportPDF = () => {
    if (!selectedUser) return;
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

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)', padding: '20px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ background: cardBg, borderRadius: '24px', padding: '20px 30px', marginBottom: '25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '28px', color: textColor }}>🏥 Medical Health Tracker</h1>
            <p style={{ margin: '5px 0 0', color: textColor }}>AI-Powered Healthcare Assistant</p>
          </div>
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <button onClick={toggleTheme} style={{ background: 'rgba(0,0,0,0.1)', border: 'none', borderRadius: '50%', width: '40px', height: '40px', fontSize: '20px', cursor: 'pointer', color: textColor }}>{isDarkMode ? '☀️' : '🌙'}</button>
            <div style={{ background: '#10b981', padding: '6px 16px', borderRadius: '50px', color: 'white', fontSize: '13px', fontWeight: '600' }}>✅ API: Healthy</div>
          </div>
        </div>

        {/* Main Content */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' }}>
          
          {/* Patient Selection */}
          <div style={{ background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' }}>
            <h2 style={{ color: textColor, marginBottom: '20px' }}>👤 Select Patient</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', maxHeight: '400px', overflowY: 'auto' }}>
              {USERS.map(user => (
                <button key={user.id} onClick={() => setSelectedUser(user)} style={{ padding: '8px 18px', background: selectedUser?.id === user.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : '#f3f4f6', color: selectedUser?.id === user.id ? 'white' : textColor, border: 'none', borderRadius: '50px', cursor: 'pointer', fontSize: '13px', margin: '4px' }}>
                  {user.name} ({user.condition})
                </button>
              ))}
            </div>
            {selectedUser && (
              <div style={{ marginTop: '15px', padding: '12px', background: 'rgba(16,185,129,0.1)', borderRadius: '12px' }}>
                <span style={{ color: '#059669', fontWeight: '600' }}>✅ Selected: {selectedUser.name} - {selectedUser.condition}</span>
              </div>
            )}
          </div>

          {/* SOS & Reports */}
          <div style={{ background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', textAlign: 'center' }}>
            <h2 style={{ color: textColor, marginBottom: '20px' }}>🚨 Emergency SOS</h2>
            <button onClick={sendSOS} style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', padding: '16px 40px', fontSize: '18px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(239,68,68,0.3)' }}>🚨 SOS EMERGENCY</button>
            <button onClick={exportPDF} style={{ marginTop: '15px', padding: '10px 20px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' }}>📄 Export PDF Report</button>
          </div>
        </div>

        {/* Health Metrics Display */}
        {selectedUser && (
          <div style={{ background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)', marginBottom: '25px' }}>
            <h2 style={{ color: textColor, marginBottom: '20px' }}>📊 Current Health Metrics - {selectedUser.name}</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '15px', marginBottom: '20px' }}>
              <div style={{ textAlign: 'center', padding: '15px', background: isDarkMode ? '#334155' : '#f3f4f6', borderRadius: '12px' }}>
                <div style={{ fontSize: '14px', color: textColor }}>🩸 Blood Pressure</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>{selectedUser.bp}</div>
                <div style={{ fontSize: '12px', color: '#9ca3af' }}>mmHg</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', background: isDarkMode ? '#334155' : '#f3f4f6', borderRadius: '12px' }}>
                <div style={{ fontSize: '14px', color: textColor }}>💓 Heart Rate</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>{selectedUser.hr}</div>
                <div style={{ fontSize: '12px', color: '#9ca3af' }}>BPM</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', background: isDarkMode ? '#334155' : '#f3f4f6', borderRadius: '12px' }}>
                <div style={{ fontSize: '14px', color: textColor }}>🩸 Blood Sugar</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>{selectedUser.sugar}</div>
                <div style={{ fontSize: '12px', color: '#9ca3af' }}>mg/dL</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', background: isDarkMode ? '#334155' : '#f3f4f6', borderRadius: '12px' }}>
                <div style={{ fontSize: '14px', color: textColor }}>⚖️ Weight</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>{selectedUser.weight}</div>
                <div style={{ fontSize: '12px', color: '#9ca3af' }}>kg</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', background: isDarkMode ? '#334155' : '#f3f4f6', borderRadius: '12px' }}>
                <div style={{ fontSize: '14px', color: textColor }}>🏥 Condition</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#f59e0b' }}>{selectedUser.condition}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={analyzeRisk} style={{ padding: '12px 24px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' }}>📊 Analyze Health Risk</button>
              <button onClick={loadHealthTips} style={{ padding: '12px 24px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' }}>💡 Get Health Tips</button>
            </div>
            
            {riskResult && (
              <div style={{ marginTop: '20px', padding: '18px', borderRadius: '16px', background: riskResult.risk_level === 'HIGH' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)' }}>
                <h4 style={{ margin: 0, color: riskResult.risk_level === 'HIGH' ? '#dc2626' : '#059669' }}>⚠️ Risk Level: {riskResult.risk_level}</h4>
                <p style={{ margin: '8px 0', color: textColor }}><strong>Issues:</strong> {riskResult.risks?.join(', ') || 'None'}</p>
                <p style={{ margin: 0, color: textColor }}><strong>Recommendations:</strong> {riskResult.recommendations?.join('; ') || 'Continue monitoring'}</p>
              </div>
            )}

            {showTips && healthTips.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ color: textColor }}>💡 Personalized Health Tips</h3>
                {healthTips.map((tip, i) => (
                  <div key={i} style={{ padding: '12px', marginBottom: '8px', background: 'rgba(16,185,129,0.08)', borderRadius: '12px', color: isDarkMode ? '#86efac' : '#065f46', borderLeft: '4px solid #10b981' }}>{tip}</div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* AI Chat */}
        <div style={{ background: cardBg, borderRadius: '24px', padding: '25px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' }}>
          <h2 style={{ color: textColor, marginBottom: '20px' }}>🤖 AI Health Assistant</h2>
          {selectedUser ? (
            <>
              <div style={{ height: '250px', overflowY: 'auto', background: isDarkMode ? '#0f172a' : '#f9fafb', borderRadius: '16px', padding: '15px', marginBottom: '15px', border: `1px solid ${borderColor}` }}>
                {chatMessages.length === 0 && <div style={{ textAlign: 'center', color: '#9ca3af', padding: '40px' }}>💬 Ask me about {selectedUser.name}'s health condition!</div>}
                {chatMessages.map((msg, idx) => (
                  <div key={idx} style={{ marginBottom: '12px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                    <div style={{ display: 'inline-block', maxWidth: '80%', padding: '10px 16px', borderRadius: '20px', background: msg.role === 'user' ? 'linear-gradient(135deg, #667eea, #764ba2)' : isDarkMode ? '#334155' : 'white', color: msg.role === 'user' ? 'white' : textColor }}>
                      <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
                    </div>
                  </div>
                ))}
                {isLoading && <div style={{ textAlign: 'left' }}><div style={{ display: 'inline-block', padding: '10px 16px', borderRadius: '20px', background: isDarkMode ? '#334155' : '#f3f4f6', color: '#9ca3af' }}>AI is thinking...</div></div>}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <input type="text" placeholder={`Ask about ${selectedUser.name}'s condition...`} value={aiQuestion} onChange={(e) => setAiQuestion(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && askAI()} style={{ flex: 1, padding: '12px', border: `1px solid ${borderColor}`, borderRadius: '12px', background: isDarkMode ? '#334155' : 'white', color: textColor }} />
                <button onClick={askAI} disabled={isLoading} style={{ padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '600' }}>Send</button>
              </div>
            </>
          ) : <div style={{ textAlign: 'center', padding: '60px', color: '#9ca3af' }}>👤 Please select a patient first</div>}
        </div>
      </div>
    </div>
  );
}

export default App;
