import React, { useState } from 'react';
const SOSButton = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const sendSOS = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/sos', { method: 'POST' });
      const data = await res.json();
      setMessage(data.status === 'sent' ? '✅ SOS Sent!' : '❌ Failed');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) { setMessage('❌ Error'); } finally { setLoading(false); }
  };
  return React.createElement('div', null,
    React.createElement('button', { onClick: sendSOS, disabled: loading, style: { backgroundColor: '#dc2626', color: 'white', padding: '20px 40px', fontSize: '24px', fontWeight: 'bold', border: 'none', borderRadius: '50px', cursor: loading ? 'not-allowed' : 'pointer' } }, loading ? 'Sending...' : '🚨 SOS'),
    message && React.createElement('div', { style: { marginTop: '10px', color: message.includes('✅') ? 'green' : 'red' } }, message)
  );
};
export default SOSButton;
