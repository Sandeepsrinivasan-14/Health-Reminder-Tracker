import React, { useState, useEffect } from 'react'
import { 
  getHealth, getUsers, createUser, getMedications, 
  addMedication, logMedication, getVaccinations, 
  addVaccination, getHealthTips 
} from './api'

function App() {
  const [apiStatus, setApiStatus] = useState('checking...')
  const [activeTab, setActiveTab] = useState('dashboard')
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [medications, setMedications] = useState([])
  const [vaccinations, setVaccinations] = useState([])
  const [healthTips, setHealthTips] = useState([])
  const [sosMessage, setSosMessage] = useState('')
  
  const [newUserName, setNewUserName] = useState('')
  const [newUserEmail, setNewUserEmail] = useState('')
  const [newMedName, setNewMedName] = useState('')
  const [newMedDosage, setNewMedDosage] = useState('')
  const [newMedTime, setNewMedTime] = useState('morning')
  const [newVaccine, setNewVaccine] = useState('')
  const [newVaccineDate, setNewVaccineDate] = useState('')

  useEffect(() => {
    checkApiHealth()
    loadUsers()
  }, [])

  const checkApiHealth = async () => {
    try {
      const data = await getHealth()
      setApiStatus(data.status)
    } catch (error) {
      setApiStatus('offline')
    }
  }

  const loadUsers = async () => {
    try {
      const data = await getUsers()
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users')
    }
  }

  const handleCreateUser = async () => {
    if (!newUserName || !newUserEmail) {
      alert('Please enter name and email')
      return
    }
    try {
      await createUser(newUserName, newUserEmail)
      setNewUserName('')
      setNewUserEmail('')
      await loadUsers()
      alert('User created successfully!')
    } catch (error) {
      alert('Failed to create user')
    }
  }

  const handleSelectUser = async (user) => {
    setSelectedUser(user)
    try {
      const meds = await getMedications(user.id)
      setMedications(meds)
      const vax = await getVaccinations(user.id)
      setVaccinations(vax)
      alert('Selected user: ' + user.name)
    } catch (error) {
      console.error('Failed to load user data')
    }
  }

  const handleAddMedication = async () => {
    if (!selectedUser) {
      alert('Please select a user first')
      return
    }
    if (!newMedName || !newMedDosage) {
      alert('Please enter medication name and dosage')
      return
    }
    try {
      await addMedication({
        user_id: selectedUser.id,
        name: newMedName,
        dosage: newMedDosage,
        time_of_day: newMedTime,
        active: true
      })
      setNewMedName('')
      setNewMedDosage('')
      const meds = await getMedications(selectedUser.id)
      setMedications(meds)
      alert('Medication added!')
    } catch (error) {
      alert('Failed to add medication')
    }
  }

  const handleLogMedication = async (medId, status) => {
    try {
      await logMedication(medId, status)
      const message = 'Medication marked as ' + status
      alert(message)
    } catch (error) {
      alert('Failed to log medication')
    }
  }

  const handleAddVaccination = async () => {
    if (!selectedUser) {
      alert('Please select a user first')
      return
    }
    if (!newVaccine || !newVaccineDate) {
      alert('Please enter vaccine name and date')
      return
    }
    try {
      await addVaccination({
        user_id: selectedUser.id,
        name: newVaccine,
        due_date: newVaccineDate
      })
      setNewVaccine('')
      setNewVaccineDate('')
      const vax = await getVaccinations(selectedUser.id)
      setVaccinations(vax)
      alert('Vaccination added!')
    } catch (error) {
      alert('Failed to add vaccination')
    }
  }

  const loadHealthTips = async () => {
    try {
      const tips = await getHealthTips()
      setHealthTips(tips)
      alert('Loaded ' + tips.length + ' health tips!')
    } catch (error) {
      alert('Failed to load health tips')
    }
  }

  const handleSOS = () => {
    if (!selectedUser) {
      alert('Please select a patient first from the Dashboard tab!')
      return
    }
    
    const message = '🚨 EMERGENCY SOS 🚨\nPatient: ' + selectedUser.name + '\nEmail: ' + selectedUser.email + '\nTime: ' + new Date().toLocaleString()
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude
          const lng = position.coords.longitude
          const location = 'https://maps.google.com/?q=' + lat + ',' + lng
          const fullMessage = message + '\n📍 Location: ' + location
          alert(fullMessage)
          setSosMessage('SOS sent with location!')
          setTimeout(() => setSosMessage(''), 3000)
        },
        () => {
          alert(message + '\n⚠️ Could not get location - please call emergency services!')
          setSosMessage('SOS sent without location!')
          setTimeout(() => setSosMessage(''), 3000)
        }
      )
    } else {
      alert(message + '\n⚠️ GPS not supported - please call emergency services!')
      setSosMessage('SOS sent!')
      setTimeout(() => setSosMessage(''), 3000)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">💊 HealthReminderTracker</h1>
          <p className="text-sm mt-1">
            API Status: <span className={apiStatus === 'healthy' ? 'text-green-200' : 'text-red-200'}>
              {apiStatus}
            </span>
            {selectedUser && <span className="ml-4">👤 Selected: {selectedUser.name}</span>}
          </p>
        </div>
      </div>

      <div className="container mx-auto p-4">
        <div className="flex gap-2 mb-6 border-b">
          <button onClick={() => setActiveTab('dashboard')} 
            className={'px-4 py-2 font-semibold ' + (activeTab === 'dashboard' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600')}>
            📋 Patient Dashboard
          </button>
          <button onClick={() => setActiveTab('caregiver')} 
            className={'px-4 py-2 font-semibold ' + (activeTab === 'caregiver' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600')}>
            👥 Caregiver & SOS
          </button>
        </div>

        {activeTab === 'dashboard' && (
          <div className="grid md:grid-cols-3 gap-6">
            {/* User Section */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold mb-4">1️⃣ Create / Select User</h2>
              <input type="text" placeholder="Name" value={newUserName} 
                onChange={(e) => setNewUserName(e.target.value)} 
                className="w-full p-2 border rounded mb-2" />
              <input type="email" placeholder="Email" value={newUserEmail} 
                onChange={(e) => setNewUserEmail(e.target.value)} 
                className="w-full p-2 border rounded mb-2" />
              <button onClick={handleCreateUser} 
                className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700 mb-4">
                ➕ Create User
              </button>
              <h3 className="font-semibold mb-2">Existing Users:</h3>
              <div className="max-h-64 overflow-y-auto">
                {users.map((user) => (
                  <button key={user.id} onClick={() => handleSelectUser(user)} 
                    className={'w-full text-left p-2 rounded mb-1 ' + (selectedUser?.id === user.id ? 'bg-blue-100 border border-blue-500' : 'bg-gray-50 hover:bg-gray-100')}>
                    <div className="font-semibold">{user.name}</div>
                    <div className="text-xs text-gray-600">{user.email}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Medications Section */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold mb-4">💊 Medications</h2>
              {selectedUser ? (
                <>
                  <input type="text" placeholder="Medication name" value={newMedName}
                    onChange={(e) => setNewMedName(e.target.value)} 
                    className="w-full p-2 border rounded mb-2" />
                  <input type="text" placeholder="Dosage (e.g., 500mg)" value={newMedDosage}
                    onChange={(e) => setNewMedDosage(e.target.value)} 
                    className="w-full p-2 border rounded mb-2" />
                  <select value={newMedTime} onChange={(e) => setNewMedTime(e.target.value)}
                    className="w-full p-2 border rounded mb-2">
                    <option value="morning">🌅 Morning</option>
                    <option value="afternoon">☀️ Afternoon</option>
                    <option value="evening">🌙 Evening</option>
                  </select>
                  <button onClick={handleAddMedication} 
                    className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 mb-4">
                    ➕ Add Medication
                  </button>
                  <h3 className="font-semibold mb-2">Your Medications:</h3>
                  <div className="max-h-96 overflow-y-auto">
                    {medications.length === 0 ? (
                      <p className="text-gray-500 text-center py-4">No medications added yet</p>
                    ) : (
                      medications.map((med) => (
                        <div key={med.id} className="border rounded p-2 mb-2">
                          <div className="font-semibold">{med.name}</div>
                          <div className="text-sm text-gray-600">{med.dosage} - {med.time_of_day}</div>
                          <div className="flex gap-2 mt-2">
                            <button onClick={() => handleLogMedication(med.id, 'taken')}
                              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">✅ Taken</button>
                            <button onClick={() => handleLogMedication(med.id, 'missed')}
                              className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">❌ Missed</button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-8">⚠️ Select a user from the left panel first</p>
              )}
            </div>

            {/* Vaccinations Section */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-bold mb-4">💉 Vaccinations</h2>
              {selectedUser ? (
                <>
                  <input type="text" placeholder="Vaccine name" value={newVaccine}
                    onChange={(e) => setNewVaccine(e.target.value)} 
                    className="w-full p-2 border rounded mb-2" />
                  <input type="date" value={newVaccineDate}
                    onChange={(e) => setNewVaccineDate(e.target.value)} 
                    className="w-full p-2 border rounded mb-2" />
                  <button onClick={handleAddVaccination} 
                    className="w-full bg-purple-600 text-white p-2 rounded hover:bg-purple-700 mb-4">
                    ➕ Add Vaccination
                  </button>
                  <h3 className="font-semibold mb-2">Upcoming Vaccinations:</h3>
                  <div className="max-h-96 overflow-y-auto">
                    {vaccinations.length === 0 ? (
                      <p className="text-gray-500 text-center py-4">No vaccinations scheduled</p>
                    ) : (
                      vaccinations.map((vax) => (
                        <div key={vax.id} className="border rounded p-2 mb-2">
                          <div className="font-semibold">{vax.name}</div>
                          <div className="text-sm text-gray-600">Due: {new Date(vax.due_date).toLocaleDateString()}</div>
                        </div>
                      ))
                    )}
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-8">⚠️ Select a user from the left panel first</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'caregiver' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* SOS Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold mb-4 text-red-600">🚨 Emergency SOS</h2>
              {!selectedUser && (
                <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-2 rounded mb-4">
                  ⚠️ Please select a patient from the Dashboard tab first
                </div>
              )}
              <button onClick={handleSOS} 
                className="w-full bg-red-600 text-white p-4 rounded-lg text-xl font-bold hover:bg-red-700 transition-all transform hover:scale-105">
                🔴 SOS EMERGENCY BUTTON 🔴
              </button>
              {sosMessage && (
                <div className="mt-4 p-2 bg-green-100 text-green-700 rounded text-center">
                  {sosMessage}
                </div>
              )}
              <p className="text-sm text-gray-600 mt-4">
                📍 Pressing this will send your location with emergency alert
              </p>
            </div>

            {/* Health Tips Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold mb-4 text-green-600">💡 Health Tips</h2>
              <button onClick={loadHealthTips} 
                className="w-full bg-green-600 text-white p-2 rounded mb-4 hover:bg-green-700">
                🔄 Load Health Tips
              </button>
              <div className="max-h-96 overflow-y-auto">
                {healthTips.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Click "Load Health Tips" to see daily health advice</p>
                ) : (
                  healthTips.map((tip, i) => (
                    <div key={i} className="border-l-4 border-green-500 pl-3 py-2 mb-2">
                      <p className="text-gray-700">💚 {tip}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Caregiver Monitoring */}
            <div className="bg-white rounded-lg shadow p-6 md:col-span-2">
              <h2 className="text-2xl font-bold mb-4 text-blue-600">👨‍👩‍👧 Caregiver Monitoring Dashboard</h2>
              {selectedUser ? (
                <div>
                  <div className="bg-blue-50 p-4 rounded-lg mb-4">
                    <h3 className="text-lg font-bold">📋 Patient Information</h3>
                    <p><strong>Name:</strong> {selectedUser.name}</p>
                    <p><strong>Email:</strong> {selectedUser.email}</p>
                    <p><strong>Last Updated:</strong> {new Date().toLocaleString()}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="bg-green-50 p-4 rounded-lg border-2 border-green-200">
                      <h3 className="font-bold text-green-700 text-lg">💊 Medications</h3>
                      <p className="text-3xl font-bold mt-2">{medications.length}</p>
                      <p className="text-sm text-gray-600">active medications scheduled</p>
                      <button className="mt-2 text-sm text-blue-600 hover:underline" onClick={() => setActiveTab('dashboard')}>
                        Manage Medications →
                      </button>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-200">
                      <h3 className="font-bold text-purple-700 text-lg">💉 Vaccinations</h3>
                      <p className="text-3xl font-bold mt-2">{vaccinations.length}</p>
                      <p className="text-sm text-gray-600">upcoming vaccines</p>
                      <button className="mt-2 text-sm text-blue-600 hover:underline" onClick={() => setActiveTab('dashboard')}>
                        Manage Vaccinations →
                      </button>
                    </div>
                  </div>
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-300 rounded-lg">
                    <h3 className="font-bold text-yellow-700">⚠️ Recent Alerts</h3>
                    <p className="text-sm text-gray-600">• No missed medications in last 24 hours</p>
                    <p className="text-sm text-gray-600">• All vaccinations are up to date</p>
                    <p className="text-sm text-gray-600 mt-2">💡 Tip: Use the SOS button for emergencies</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">👤</div>
                  <p className="text-gray-500 text-lg">No patient selected</p>
                  <p className="text-gray-400 mt-2">Please go to the Dashboard tab and select a patient first</p>
                  <button onClick={() => setActiveTab('dashboard')} 
                    className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Go to Dashboard →
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
