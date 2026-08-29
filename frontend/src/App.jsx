import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
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
  const { token, user } = useAuthStore()

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {token ? (
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/analysis" element={user?.role === 'employee' ? <AnalysisPage /> : <Navigate to="/" replace />} />
            <Route path="/reports/new" element={user?.role === 'employee' ? <NewReportPage /> : <Navigate to="/" replace />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/reports/:id" element={<ReportDetailPage />} />
            <Route path="/reports/:id/edit" element={<EditReportPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/taxonomy" element={<TaxonomyPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </Router>
  )
}

export default App
