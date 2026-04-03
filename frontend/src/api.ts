const API_URL = 'http://localhost:8000'

export async function getHealth() {
  const res = await fetch(API_URL + '/health')
  return res.json()
}

export async function getUsers() {
  const res = await fetch(API_URL + '/users')
  return res.json()
}

export async function createUser(name, email) {
  const res = await fetch(API_URL + '/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email }),
  })
  return res.json()
}

export async function getMedications(userId) {
  const res = await fetch(API_URL + '/medications/user/' + userId)
  return res.json()
}

export async function addMedication(data) {
  const res = await fetch(API_URL + '/medications', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function logMedication(medId, status) {
  const res = await fetch(API_URL + '/medications/' + medId + '/log?status=' + status, {
    method: 'POST'
  })
  return res.json()
}

export async function getVaccinations(userId) {
  const res = await fetch(API_URL + '/vaccinations/user/' + userId)
  return res.json()
}

export async function addVaccination(data) {
  const res = await fetch(API_URL + '/vaccinations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function getHealthTips() {
  const res = await fetch(API_URL + '/health-tips')
  return res.json()
}
