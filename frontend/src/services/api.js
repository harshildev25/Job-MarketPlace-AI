import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })

        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)

        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => api.post('/api/v1/auth/register', data),
  login: (data) => api.post('/api/v1/auth/login', data),
  refresh: (refreshToken) => api.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
  logout: () => api.post('/api/v1/auth/logout'),
}

export const jobsAPI = {
  list: () => api.get('/api/v1/jobs'),
  get: (id) => api.get(`/api/v1/jobs/${id}`),
  create: (data) => api.post('/api/v1/jobs', data),
  update: (id, data) => api.put(`/api/v1/jobs/${id}`, data),
  delete: (id) => api.delete(`/api/v1/jobs/${id}`),
}

export const candidatesAPI = {
  getProfile: () => api.get('/api/v1/candidates/profile'),
  uploadResume: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/v1/candidates/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getRecommendations: () => api.get('/api/v1/candidates/recommendations'),
}

export default api
