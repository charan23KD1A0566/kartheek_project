import CursorFX from './components/CursorFX'
import VisualEffects from './components/VisualEffects'
import { MemoryRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/appStore'

import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import NewReportPage from './pages/NewReportPage'
import AnalysisPage from './pages/AnalysisPage'
import ReportsPage from './pages/ReportsPage'
import ReportDetailPage from './pages/ReportDetailPage'
import EditReportPage from './pages/EditReportPage'
import AnalyticsPage from './pages/AnalyticsPage'
import TaxonomyPage from './pages/TaxonomyPage'
import Layout from './components/Layout'

function App() {
  const { isAuthenticated, user } = useAuthStore()

  return (
    <Router>
      {/* =====================================================
          GLOBAL VISUAL EFFECTS
          Cursor glow, cursor trail, click ripple,
          particle/firework effects and other UI effects
          ===================================================== */}
      <VisualEffects />

      <Routes>
        {/* =====================================================
            LOGIN
            ===================================================== */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
        />

        {/* =====================================================
            AUTHENTICATED APPLICATION
            ===================================================== */}
        {isAuthenticated ? (
          <Route element={<Layout />}>

            {/* Dashboard */}
            <Route
              path="/"
              element={<DashboardPage />}
            />

            {/* =================================================
                ANALYSIS
                Employee-only
                ================================================= */}
            <Route
              path="/analysis"
              element={
                user?.role === 'EMPLOYEE' ? (
                  <AnalysisPage />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* =================================================
                NEW REPORT
                Employee-only
                ================================================= */}
            <Route
              path="/reports/new"
              element={
                user?.role === 'EMPLOYEE' ? (
                  <NewReportPage />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* =================================================
                REPORTS
                ================================================= */}
            <Route
              path="/reports"
              element={<ReportsPage />}
            />

            {/* =================================================
                REPORT DETAILS
                ================================================= */}
            <Route
              path="/reports/:id"
              element={<ReportDetailPage />}
            />

            {/* =================================================
                EDIT REPORT
                ================================================= */}
            <Route
              path="/reports/:id/edit"
              element={<EditReportPage />}
            />

            {/* =================================================
                ANALYTICS
                ================================================= */}
            <Route
              path="/analytics"
              element={<AnalyticsPage />}
            />

            {/* =================================================
                TAXONOMY
                ================================================= */}
            <Route
              path="/taxonomy"
              element={<TaxonomyPage />}
            />

            {/* =================================================
                UNKNOWN AUTHENTICATED ROUTE
                ================================================= */}
            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />

          </Route>
        ) : (
          /* ===================================================
             NOT AUTHENTICATED
             Redirect everything to login
             =================================================== */
          <Route
            path="*"
            element={<Navigate to="/login" replace />}
          />
        )}
      </Routes>
    </Router>
  )
}

export default App