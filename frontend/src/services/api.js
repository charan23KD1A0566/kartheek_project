import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
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

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth endpoints
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
}

// Analysis endpoints
export const analysisAPI = {
  analyze: (text, reportType, location) =>
    api.post('/analyze', { text, report_type: reportType, location }),
  
  createAndAnalyze: (reportData) =>
    api.post('/reports', reportData),
}

// Reports endpoints
export const reportsAPI = {
  getReports: (skip = 0, limit = 20, sifStatus = null, riskLevel = null) => {
    const params = new URLSearchParams({ skip, limit })
    if (sifStatus) params.append('sif_status', sifStatus)
    if (riskLevel) params.append('risk_level', riskLevel)
    return api.get(`/reports?${params}`)
  },
  
  getReportDetail: (reportId) =>
    api.get(`/reports/${reportId}`),

  updateReport: (reportId, reportData) =>
    api.put(`/reports/${reportId}`, reportData),
  
  validateReport: (reportId, validationData) =>
    api.post(`/reports/${reportId}/validate`, validationData),
}

// Dashboard endpoints
export const dashboardAPI = {
  getStats: () => api.get('/dashboard'),
}

// Analytics endpoints
export const analyticsAPI = {
  getAnalytics: () => api.get('/analytics'),
}

// Taxonomy endpoints
export const taxonomyAPI = {
  getTaxonomy: () => api.get('/taxonomy'),
}

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
}

export const alertsAPI = {
  getAlerts: () => api.get('/alerts'),
  getUnread: () => api.get('/alerts/unread'),
  markRead: (alertId) => api.post(`/alerts/${alertId}/read`),
}

export default api
