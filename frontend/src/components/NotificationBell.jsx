import React, { useState, useEffect } from 'react';
const NotificationBell = ({ userId }) => {
  const [alerts, setAlerts] = useState([]);
  useEffect(() => {
    if (userId) fetch(`http://localhost:8000/api/notifications/alerts/${userId}`).then(r => r.json()).then(setAlerts);
    const interval = setInterval(() => fetch(`http://localhost:8000/api/notifications/alerts/${userId}`).then(r => r.json()).then(setAlerts), 30000);
    return () => clearInterval(interval);
  }, [userId]);
  const unread = alerts.filter(a => !a.acknowledged).length;
  const [show, setShow] = useState(false);
  const acknowledge = async (id) => {
    await fetch(`http://localhost:8000/api/notifications/alerts/${id}/acknowledge`, { method: 'PUT' });
    setAlerts(alerts.map(a => a.id === id ? { ...a, acknowledged: true } : a));
  };
  return React.createElement('div', { style: { position: 'relative' } },
    React.createElement('button', { onClick: () => setShow(!show), style: { padding: '8px', background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' } }, '🔔', unread > 0 && React.createElement('span', { style: { position: 'absolute', top: '-5px', right: '-5px', background: 'red', color: 'white', borderRadius: '50%', padding: '2px 6px', fontSize: '12px' } }, unread)),
    show && React.createElement('div', { style: { position: 'absolute', right: 0, top: '40px', width: '300px', background: 'white', border: '1px solid #ddd', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', zIndex: 1000, maxHeight: '400px', overflow: 'auto' } },
      React.createElement('div', { style: { padding: '10px', borderBottom: '1px solid #ddd', fontWeight: 'bold' } }, 'Notifications'),
      alerts.length === 0 ? React.createElement('div', { style: { padding: '20px', textAlign: 'center', color: '#666' } }, 'No alerts') :
        alerts.map(alert => React.createElement('div', { key: alert.id, style: { padding: '10px', borderBottom: '1px solid #eee' } },
          React.createElement('div', { style: { fontWeight: 'bold', color: alert.level === 'danger' ? 'red' : alert.level === 'warning' ? 'orange' : 'blue' } }, alert.type),
          React.createElement('div', { style: { fontSize: '12px', color: '#666' } }, alert.message),
          React.createElement('div', { style: { fontSize: '10px', color: '#999', marginTop: '5px' } }, new Date(alert.created_at).toLocaleString()),
          !alert.acknowledged && React.createElement('button', { onClick: () => acknowledge(alert.id), style: { marginTop: '5px', padding: '2px 8px', fontSize: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' } }, 'Mark Read')
        ))
    )
  );
};
export default NotificationBell;
