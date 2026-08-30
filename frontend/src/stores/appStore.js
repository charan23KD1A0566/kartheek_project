import { create } from 'zustand'

// Initialize from localStorage
const getInitialUser = () => {
  try {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

const getInitialToken = () => {
  try {
    return localStorage.getItem('access_token')
  } catch {
    return null
  }
}

export const useAuthStore = create((set) => ({
  user: getInitialUser(),
  token: getInitialToken(),
  isAuthenticated: Boolean(getInitialToken() && getInitialUser()),
  isLoading: false,
  error: null,

  setUser: (user, token) => {
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('access_token', token)
    set({ user, token, isAuthenticated: true, error: null })
  },

  logout: () => {
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}))

export const useAnalysisStore = create((set) => ({
  currentReport: null,
  currentAnalysis: null,
  isAnalyzing: false,
  error: null,

  setReport: (report) => set({ currentReport: report }),
  setAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  reset: () =>
    set({
      currentReport: null,
      currentAnalysis: null,
      isAnalyzing: false,
      error: null,
    }),
}))

export const useDashboardStore = create((set) => ({
  stats: null,
  isLoading: false,
  error: null,

  setStats: (stats) => set({ stats }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}))
