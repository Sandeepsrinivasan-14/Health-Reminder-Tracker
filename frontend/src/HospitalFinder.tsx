import React, { useState } from 'react'

interface Location {
  lat: number
  lng: number
}

function HospitalFinder() {
  const [location, setLocation] = useState<Location | null>(null)
  const [loading, setLoading] = useState(false)
  const [hospitals, setHospitals] = useState<any[]>([])

  const getCurrentLocation = () => {
    setLoading(true)
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          }
          setLocation(loc)
          searchNearbyHospitals(loc)
        },
        (error) => {
          alert('Unable to get location: ' + error.message)
          setLoading(false)
        }
      )
    } else {
      alert('Geolocation is not supported by this browser')
      setLoading(false)
    }
  }

  const searchNearbyHospitals = (loc: Location) => {
    // Simulated hospital data (in real app, use Google Places API)
    const mockHospitals = [
      { name: 'City General Hospital', distance: '0.5 km', phone: '+91 9876543210' },
      { name: 'Apollo Medical Center', distance: '1.2 km', phone: '+91 9876543211' },
      { name: 'Fortis Healthcare', distance: '2.0 km', phone: '+91 9876543212' },
      { name: 'Government Hospital', distance: '2.5 km', phone: '+91 9876543213' },
      { name: 'Medicare Clinic', distance: '3.0 km', phone: '+91 9876543214' }
    ]
    setHospitals(mockHospitals)
    setLoading(false)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mt-4">
      <h2 className="text-xl font-bold mb-4 text-blue-600">Nearby Hospitals & Pharmacies</h2>
      <button
        onClick={getCurrentLocation}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mb-4"
      >
        {loading ? 'Getting Location...' : 'Find Nearby Hospitals'}
      </button>
      
      {location && (
        <p className="text-sm text-gray-600 mb-2">
          Location: {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
        </p>
      )}
      
      {hospitals.length > 0 && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Nearby Healthcare Facilities:</h3>
          {hospitals.map((hospital, i) => (
            <div key={i} className="border rounded p-3 mb-2">
              <div className="font-semibold">{hospital.name}</div>
              <div className="text-sm text-gray-600">Distance: {hospital.distance}</div>
              <div className="text-sm text-gray-600">Phone: {hospital.phone}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default HospitalFinder
