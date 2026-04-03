import React, { useState } from 'react';
const HealthTips = () => {
  const [tips, setTips] = useState([]);
  const loadTips = async () => {
    const res = await fetch('http://localhost:8000/health-tips');
    setTips(await res.json());
  };
  return React.createElement('div', null,
    React.createElement('button', { onClick: loadTips, style: { backgroundColor: '#3b82f6', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '8px', marginBottom: '20px' } }, '📋 Load Health Tips'),
    tips.length > 0 && React.createElement('div', { style: { backgroundColor: '#f3f4f6', padding: '20px', borderRadius: '8px' } },
      React.createElement('h3', null, '💡 Health Tips'),
      tips.map((tip, i) => React.createElement('div', { key: i, style: { padding: '10px', margin: '5px 0', backgroundColor: 'white', borderRadius: '8px' } }, '✓ ', tip))
    )
  );
};
export default HealthTips;
