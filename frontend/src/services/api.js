import axios from 'axios'

const runtimeBaseURL = typeof window !== 'undefined' ? window.API_CONFIG?.baseURL : null
const API_BASE_URL = runtimeBaseURL || import.meta.env.VITE_API_URL || '/api'

console.log('[API] Configured base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token && !config.url?.includes('/auth/login') && !config.url?.includes('/auth/register')) {
    config.headers.Authorization = `Bearer ${token}`
  }
  console.log(`[API ${config.method.toUpperCase()}] ${config.url}`)
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response received: ${response.status}`)
    return response
  },
  (error) => {
    console.error('[API] Error:', error.message)
    console.error('[API] Response status:', error.response?.status)
    console.error('[API] Response data:', error.response?.data)
    
    const isAuthRequest = error.config?.url?.includes('/auth/login') || error.config?.url?.includes('/auth/register')
    if (error.response?.status === 401 && !isAuthRequest) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth endpoints
export const authAPI = {
  login: (email, password) => {
    console.log('[AUTH] Logging in with:', email)
    return api.post('/auth/login', { email, password })
  },
  
  register: (name, email, password, confirm_password) => {
    return api.post('/auth/register', { name, email, password, confirm_password, role: 'EMPLOYEE' })
  },
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
