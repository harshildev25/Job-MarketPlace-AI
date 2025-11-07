import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export const Dashboard = () => {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">TalentIQ Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Welcome, {user?.name}!</h2>
          <p className="text-gray-600 mb-4">Email: {user?.email}</p>
          <p className="text-gray-600 mb-4">
            Role: <span className="font-bold capitalize">{user?.role}</span>
          </p>

          <div className="mt-8 grid grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-blue-600">0</h3>
              <p className="text-gray-600">Active Jobs</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-green-600">0</h3>
              <p className="text-gray-600">Applications</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-purple-600">0</h3>
              <p className="text-gray-600">Candidates</p>
            </div>
          </div>

          <p className="text-gray-500 mt-8 text-sm">
            ✅ Week 1 MVP: Auth working! Week 2 will add job posting and candidate matching.
          </p>
        </div>
      </main>
    </div>
  )
}
