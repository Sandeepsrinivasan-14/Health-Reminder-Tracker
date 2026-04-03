import React, { useState, useEffect } from 'react';
const HealthRecords = ({ userId }) => {
  const [records, setRecords] = useState([]);
  useEffect(() => { if (userId) fetch(`http://localhost:8000/health-data/user/${userId}`).then(r => r.json()).then(setRecords); }, [userId]);
  if (!records.length) return React.createElement('div', null, 'No health data yet');
  return React.createElement('div', null,
    React.createElement('h3', null, 'Recent Health Records'),
    React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
      React.createElement('thead', null,
        React.createElement('tr', null,
          ['Date', 'BP', 'HR', 'Sugar', 'Weight'].map(h => React.createElement('th', { key: h, style: { border: '1px solid #ddd', padding: '8px', backgroundColor: '#f3f4f6' } }, h))
        )
      ),
      React.createElement('tbody', null,
        records.map((r, i) => React.createElement('tr', { key: i },
          React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, new Date(r.recorded_at).toLocaleDateString()),
          React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, `${r.bp_systolic}/${r.bp_diastolic}`),
          React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, r.heart_rate),
          React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, r.blood_sugar),
          React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, r.weight)
        ))
      )
    )
  );
};
export default HealthRecords;
