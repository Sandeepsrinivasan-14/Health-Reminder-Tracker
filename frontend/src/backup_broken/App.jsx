import React, { useMemo, useState } from "react";
import {
  FiBell,
  FiActivity,
  FiHeart,
  FiAlertTriangle,
  FiCheckCircle,
  FiClock,
  FiPlus,
  FiPhoneCall,
  FiX,
  FiEdit2,
  FiTrash2,
  FiSearch,
  FiClipboard,
  FiMessageSquare,
  FiZap
} from "react-icons/fi";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import "./index.css";

const initialReminders = [
  { id: 1, name: "Paracetamol", time: "08:00 AM", status: "Taken", note: "After breakfast", dosage: "500 mg", food: "After food", frequency: "Daily", stock: 12, priority: "Medium" },
  { id: 2, name: "Vitamin D", time: "01:00 PM", status: "Due now", note: "After lunch", dosage: "1 tablet", food: "After food", frequency: "Daily", stock: 8, priority: "Low" },
  { id: 3, name: "BP Tablet", time: "08:00 PM", status: "Upcoming", note: "Night dose", dosage: "40 mg", food: "Before food", frequency: "Daily", stock: 4, priority: "High" },
];

const initialSymptoms = [
  { id: 1, date: "2026-04-01", symptom: "Headache", severity: "Mild", note: "Morning only" },
  { id: 2, date: "2026-04-02", symptom: "Fatigue", severity: "Moderate", note: "After lunch" },
];

const vitalsData = [
  { day: "Mon", bp: 128, sugar: 106 },
  { day: "Tue", bp: 132, sugar: 110 },
  { day: "Wed", bp: 126, sugar: 101 },
  { day: "Thu", bp: 130, sugar: 108 },
  { day: "Fri", bp: 124, sugar: 99 },
];

const appointments = [
  { id: 1, doctor: "Dr. Kumar", type: "General Review", date: "2026-04-05", time: "10:30 AM" },
  { id: 2, doctor: "Dr. Priya", type: "Cardiology", date: "2026-04-12", time: "06:00 PM" },
];

const emergencyContacts = [
  { id: 1, name: "Father", phone: "+91 90000 11111" },
  { id: 2, name: "Family Doctor", phone: "+91 90000 22222" },
];

function statusClass(status) {
  if (status === "Taken") return "badge success";
  if (status === "Due now") return "badge warning";
  if (status === "Missed") return "badge danger";
  return "badge neutral";
}

export default function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [showModal, setShowModal] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  const [reminders, setReminders] = useState(initialReminders);
  const [symptoms] = useState(initialSymptoms);
  const [chatMessages, setChatMessages] = useState([
    { role: "assistant", text: "Hello. I am your AI health assistant. Ask me about reminders, symptoms, or healthy routines." }
  ]);
  const [aiTips, setAiTips] = useState([
    "Stay hydrated and avoid skipping medicine timings.",
    "Track blood pressure regularly if you are taking BP medication.",
  ]);

  const [form, setForm] = useState({
    name: "",
    time: "",
    status: "Upcoming",
    note: "",
    dosage: "",
    food: "After food",
    frequency: "Daily",
    stock: "",
    priority: "Medium",
  });

  const filteredReminders = useMemo(() => {
    return reminders.filter((item) => {
      const matchFilter = filter === "All" ? true : item.status === filter;
      const matchSearch =
        item.name.toLowerCase().includes(search.toLowerCase()) ||
        item.note.toLowerCase().includes(search.toLowerCase()) ||
        item.dosage.toLowerCase().includes(search.toLowerCase());
      return matchFilter && matchSearch;
    });
  }, [reminders, filter, search]);

  const stats = useMemo(() => {
    const taken = reminders.filter((r) => r.status === "Taken").length;
    const upcoming = reminders.filter((r) => r.status === "Upcoming").length;
    const alerts = reminders.filter((r) => r.status === "Due now" || r.status === "Missed").length;

    return [
      { title: "Today's Reminders", value: reminders.length, icon: <FiBell /> },
      { title: "Taken", value: taken, icon: <FiCheckCircle /> },
      { title: "Upcoming", value: upcoming, icon: <FiClock /> },
      { title: "Alerts", value: alerts, icon: <FiAlertTriangle /> },
    ];
  }, [reminders]);

  const resetForm = () => {
    setForm({
      name: "",
      time: "",
      status: "Upcoming",
      note: "",
      dosage: "",
      food: "After food",
      frequency: "Daily",
      stock: "",
      priority: "Medium",
    });
    setEditingId(null);
  };

  const openAddModal = () => {
    resetForm();
    setShowModal(true);
  };

  const openEditModal = (item) => {
    setForm({
      name: item.name,
      time: item.time,
      status: item.status,
      note: item.note || "",
      dosage: item.dosage || "",
      food: item.food || "After food",
      frequency: item.frequency || "Daily",
      stock: item.stock ?? "",
      priority: item.priority || "Medium",
    });
    setEditingId(item.id);
    setShowModal(true);
  };

  const handleSaveReminder = (e) => {
    e.preventDefault();

    if (!form.name.trim() || !form.time.trim()) {
      alert("Please enter medicine name and time.");
      return;
    }

    const payload = {
      name: form.name.trim(),
      time: form.time.trim(),
      status: form.status,
      note: form.note.trim(),
      dosage: form.dosage.trim(),
      food: form.food,
      frequency: form.frequency,
      stock: Number(form.stock || 0),
      priority: form.priority,
    };

    if (editingId) {
      setReminders((prev) => prev.map((item) => (item.id === editingId ? { ...item, ...payload } : item)));
    } else {
      setReminders((prev) => [{ id: Date.now(), ...payload }, ...prev]);
    }

    resetForm();
    setShowModal(false);
    setActiveTab("Reminders");
  };

  const markTaken = (id) => setReminders((prev) => prev.map((item) => (item.id === id ? { ...item, status: "Taken" } : item)));
  const markMissed = (id) => setReminders((prev) => prev.map((item) => (item.id === id ? { ...item, status: "Missed" } : item)));
  const removeReminder = (id) => setReminders((prev) => prev.filter((item) => item.id !== id));

  const triggerSOS = () => {
    alert("SOS triggered. Contacting emergency support...");
  };

  const generateAiRecommendations = () => {
    setAiLoading(true);

    setTimeout(() => {
      const dueNow = reminders.filter((r) => r.status === "Due now").length;
      const lowStock = reminders.filter((r) => r.stock <= 5).length;

      const generated = [
        dueNow > 0
          ? "You have medicines due now. Complete them on time to keep your routine stable."
          : "No immediate medicine is due now. Maintain your regular schedule.",
        lowStock > 0
          ? "Some medicines are low in stock. Plan your refill before stock runs out."
          : "Medicine stock looks stable right now.",
        symptoms.length > 0
          ? "Recent symptom logs suggest tracking patterns daily and sharing them with your doctor if they continue."
          : "No recent symptom log is present. Recording symptoms can improve AI guidance.",
      ];

      setAiTips(generated);
      setAiLoading(false);
    }, 900);
  };

  const handleSendChat = () => {
    if (!chatInput.trim()) return;

    const userText = chatInput.trim();
    const lower = userText.toLowerCase();

    let reply = "I can help with reminders, symptoms, medicines, and healthy routines.";

    if (lower.includes("bp") || lower.includes("blood pressure")) {
      reply = "Your recent BP trend looks moderately stable. Continue taking BP medicine on time and monitor at the same time daily.";
    } else if (lower.includes("sugar")) {
      reply = "Your sugar trend appears fairly controlled. Try regular meal timing and avoid missing medication.";
    } else if (lower.includes("missed")) {
      reply = "If a dose is missed, check your doctor's advice for that medicine instead of doubling the next dose.";
    } else if (lower.includes("reminder")) {
      reply = "You can review reminders, mark doses as taken or missed, and keep notes for each medicine.";
    } else if (lower.includes("health tips") || lower.includes("tips")) {
      reply = "General health tips: stay hydrated, sleep well, follow medicine timings, and log symptoms regularly.";
    }

    setChatMessages((prev) => [
      ...prev,
      { role: "user", text: userText },
      { role: "assistant", text: reply },
    ]);
    setChatInput("");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <FiHeart />
          </div>
          <div>
            <h2>Health Tracker</h2>
            <p>Care dashboard</p>
          </div>
        </div>

        <nav className="nav-links">
          {["Dashboard", "Reminders", "Records", "SOS"].map((tab) => (
            <button
              key={tab}
              className={`nav-item ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === "Dashboard" && <FiActivity />}
              {tab === "Reminders" && <FiBell />}
              {tab === "Records" && <FiClipboard />}
              {tab === "SOS" && <FiAlertTriangle />}
              {tab}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Good afternoon</p>
            <h1>Welcome back, Sandeep</h1>
            <p className="subtext">Track medicines, health logs, appointments, AI guidance, and emergency actions in one place.</p>
          </div>

          <div className="topbar-actions">
            <button className="btn btn-secondary" onClick={() => setActiveTab("Records")}>
              View records
            </button>
            <button className="btn btn-primary" onClick={openAddModal}>
              <FiPlus /> Add reminder
            </button>
          </div>
        </header>

        <section className="stats-grid">
          {stats.map((item) => (
            <article className="card stat-card" key={item.title}>
              <div className="stat-icon">{item.icon}</div>
              <div>
                <p className="muted">{item.title}</p>
                <h3>{item.value}</h3>
              </div>
            </article>
          ))}
        </section>

        {activeTab === "Dashboard" && (
          <section className="content-grid">
            <article className="card panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Medication</p>
                  <h2>Today's reminders</h2>
                </div>
                <button className="btn btn-ghost" onClick={() => setShowManage((prev) => !prev)}>
                  {showManage ? "Close manage" : "Manage"}
                </button>
              </div>

              <div className="toolbar-row">
                <div className="search-box">
                  <FiSearch />
                  <input
                    type="text"
                    placeholder="Search medicine, dosage, note"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>

                <select value={filter} onChange={(e) => setFilter(e.target.value)} className="filter-select">
                  <option>All</option>
                  <option>Taken</option>
                  <option>Upcoming</option>
                  <option>Due now</option>
                  <option>Missed</option>
                </select>
              </div>

              <div className="reminder-list">
                {filteredReminders.map((item) => (
                  <div className="reminder-item" key={item.id}>
                    <div>
                      <h3>{item.name}</h3>
                      <p className="muted">{item.time} · {item.dosage} · {item.food}</p>
                      <p className="reminder-note">{item.note}</p>
                      <p className="tiny-meta">Frequency: {item.frequency} | Stock: {item.stock} | Priority: {item.priority}</p>
                    </div>

                    <div className="reminder-actions">
                      <span className={statusClass(item.status)}>{item.status}</span>
                      {showManage && (
                        <div className="inline-actions">
                          <button className="mini-btn" onClick={() => markTaken(item.id)}>Taken</button>
                          <button className="mini-btn" onClick={() => markMissed(item.id)}>Missed</button>
                          <button className="mini-btn" onClick={() => openEditModal(item)}><FiEdit2 /></button>
                          <button className="mini-btn danger-outline" onClick={() => removeReminder(item.id)}><FiTrash2 /></button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="card panel ai-panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">AI assistant</p>
                  <h2>Health conversation</h2>
                </div>
                <button className="btn btn-primary ai-recommend-btn" onClick={generateAiRecommendations}>
                  <FiZap /> {aiLoading ? "Generating..." : "Get AI recommendations"}
                </button>
              </div>

              <div className="ai-tips-box">
                {aiTips.map((tip, index) => (
                  <div className="tip-item" key={index}>
                    <span className="tip-dot"></span>
                    <p>{tip}</p>
                  </div>
                ))}
              </div>

              <div className="chat-box">
                <div className="chat-messages">
                  {chatMessages.map((msg, index) => (
                    <div key={index} className={`chat-bubble ${msg.role}`}>
                      {msg.text}
                    </div>
                  ))}
                </div>

                <div className="chat-input-row">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask AI about reminders, symptoms, BP, or diet..."
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleSendChat();
                    }}
                  />
                  <button className="btn btn-primary" onClick={handleSendChat}>
                    <FiMessageSquare /> Send
                  </button>
                </div>
              </div>
            </article>
          </section>
        )}

        {activeTab === "Records" && (
          <section className="records-grid">
            <article className="card panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Vitals</p>
                  <h2>BP and sugar trend</h2>
                </div>
              </div>

              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={vitalsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                    <XAxis dataKey="day" stroke="#cbd5e1" />
                    <YAxis stroke="#cbd5e1" />
                    <Tooltip />
                    <Line type="monotone" dataKey="bp" stroke="#14b8a6" strokeWidth={3} />
                    <Line type="monotone" dataKey="sugar" stroke="#8b5cf6" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </article>
          </section>
        )}

        {activeTab === "SOS" && (
          <section className="records-grid">
            <article className="card panel sos-panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow danger-text">Emergency</p>
                  <h2>SOS support</h2>
                </div>
              </div>

              <p className="muted">Use this button only for urgent medical help or emergency contact access.</p>

              <button className="btn btn-danger sos-btn" onClick={triggerSOS}>
                <FiPhoneCall /> Trigger SOS
              </button>
            </article>
          </section>
        )}
      </main>

      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <div>
                <p className="eyebrow">{editingId ? "Edit entry" : "New entry"}</p>
                <h2>{editingId ? "Edit reminder" : "Add reminder"}</h2>
              </div>
              <button className="icon-btn" onClick={() => setShowModal(false)}>
                <FiX />
              </button>
            </div>

            <form className="modal-form" onSubmit={handleSaveReminder}>
              <label>
                Medicine name
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </label>

              <label>
                Time
                <input type="text" value={form.time} onChange={(e) => setForm({ ...form, time: e.target.value })} />
              </label>

              <label>
                Dosage
                <input type="text" value={form.dosage} onChange={(e) => setForm({ ...form, dosage: e.target.value })} />
              </label>

              <label>
                Food relation
                <select value={form.food} onChange={(e) => setForm({ ...form, food: e.target.value })}>
                  <option>Before food</option>
                  <option>After food</option>
                  <option>Any time</option>
                </select>
              </label>

              <label>
                Frequency
                <select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
                  <option>Daily</option>
                  <option>Twice daily</option>
                  <option>Weekly</option>
                  <option>As needed</option>
                </select>
              </label>

              <label>
                Stock
                <input type="number" value={form.stock} onChange={(e) => setForm({ ...form, stock: e.target.value })} />
              </label>

              <label>
                Priority
                <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                </select>
              </label>

              <label>
                Status
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                  <option>Upcoming</option>
                  <option>Due now</option>
                  <option>Taken</option>
                  <option>Missed</option>
                </select>
              </label>

              <label>
                Note
                <input type="text" value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
              </label>

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? "Update reminder" : "Save reminder"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
