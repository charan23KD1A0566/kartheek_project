import { useEffect, useState } from 'react'
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { analyticsAPI } from '../services/api'
import { TrendingUp, AlertTriangle } from 'lucide-react'

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await analyticsAPI.getAnalytics()
      setAnalytics(response.data)
    } catch (err) {
      setError('Failed to load analytics')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-slate-500">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (error || !analytics) {
    return (
      <div className="risk-high rounded-lg p-6 text-center">
        <p className="font-semibold">{error}</p>
        <button
          onClick={loadAnalytics}
          className="btn btn-secondary mt-4"
        >
          Try Again
        </button>
      </div>
    )
  }

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#22c55e']

  return (
    <div className="fade-in space-y-6">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="page-title flex items-center gap-3">
          <TrendingUp size={32} className="text-amber-500" />
          Analytics & Insights
        </h1>
        <p className="page-subtitle mt-2">Comprehensive analysis of safety reports, hazards, and trends.</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          label="Total Reports"
          value={analytics.total_reports}
          icon="📊"
          color="blue"
        />
        <StatCard
          label="Potential SIF %"
          value={`${analytics.sif_percentage.toFixed(1)}%`}
          icon="⚠️"
          color="amber"
        />
        <StatCard
          label="Validation Agreement"
          value={`${analytics.validation_agreement.toFixed(1)}%`}
          icon="✅"
          color="green"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Level Distribution */}
        <div className="card p-5 sm:p-6">
          <h3 className="text-lg font-bold text-slate-900">Risk level distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(analytics.risk_distribution).map(([level, count]) => ({
              name: level,
              count
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#1e3a5f" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Hazards */}
        <div className="card p-5 sm:p-6">
          <h3 className="text-lg font-bold text-slate-900">Top hazard categories</h3>
          {analytics.hazard_distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics.hazard_distribution.slice(0, 6)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ hazard, count }) => `${hazard}: ${count}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {analytics.hazard_distribution.slice(0, 6).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-steel-600 text-center py-12">No hazard data available</p>
          )}
        </div>
      </div>

      {/* Detailed Hazard Table */}
      <div className="card p-5 sm:p-6">
        <h3 className="text-lg font-bold text-slate-900">Hazard breakdown</h3>
        {analytics.hazard_distribution.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-steel-50 border-b-2 border-steel-200">
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-600">Hazard category</th>
                  <th className="px-4 py-3 text-center text-xs font-bold uppercase tracking-wider text-slate-600">Count</th>
                  <th className="px-4 py-3 text-center text-xs font-bold uppercase tracking-wider text-slate-600">Percentage</th>
                  <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-slate-600">Distribution</th>
                </tr>
              </thead>
              <tbody>
                {analytics.hazard_distribution.map((hazard, idx) => (
                  <tr key={idx} className={`border-b border-steel-200 ${idx % 2 === 0 ? 'bg-white' : 'bg-steel-50'} hover:bg-steel-100`}>
                    <td className="px-4 py-3 font-medium text-navy-700">{hazard.hazard}</td>
                    <td className="px-4 py-3 text-center text-navy-900 font-bold">{hazard.count}</td>
                    <td className="px-4 py-3 text-center text-navy-900">{hazard.percentage.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-right">
                      <div className="w-32 bg-steel-200 rounded-full h-2 mx-auto">
                        <div
                          className="bg-amber-500 h-2 rounded-full"
                          style={{
                            width: `${Math.min(100, (hazard.percentage / 100) * 100)}%`
                          }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-steel-600 text-center py-12">No hazard data available</p>
        )}
      </div>

      {/* Reports Trend */}
      <div className="card p-5 sm:p-6">
        <h3 className="text-lg font-bold text-slate-900">Reports over time</h3>
        {analytics.reports_over_time && analytics.reports_over_time.length > 0 ? (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={analytics.reports_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#1e3a5f"
                strokeWidth={2}
                name="Reports"
                dot={{ fill: '#f59e0b', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-steel-600 text-center py-12">No trend data available</p>
        )}
      </div>

      {/* Data Source Distribution */}
      <div className="card p-5 sm:p-6">
        <h3 className="text-lg font-bold text-slate-900">Data source distribution</h3>
        <div className="space-y-3">
          {Object.entries(analytics.data_source_distribution || {}).map(([source, count]) => {
            const percentage = (count / analytics.total_reports) * 100
            return (
              <div key={source} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3">
                <div className="flex-1">
                  <p className="font-medium text-navy-700 mb-1">{source}</p>
                  <div className="w-full bg-steel-300 rounded-full h-2">
                    <div
                      className="bg-navy-700 h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div className="ml-4 text-right">
                  <p className="text-lg font-bold text-navy-900">{count}</p>
                  <p className="text-xs text-steel-600">{percentage.toFixed(1)}%</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Methodology Note */}
      <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          <strong>ℹ️ Methodology:</strong> All analytics are calculated from the MongoDB database in real-time.
          Percentages and distributions are based on actual analyzed reports. This is a prototype system and
          metrics are illustrative only.
        </p>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon, color }) {
  const colors = {
    blue: 'bg-blue-50 border-blue-200',
    amber: 'bg-amber-50 border-amber-200',
    green: 'bg-green-50 border-green-200',
  }

  return (
    <div className={`card ${colors[color]} border-2 p-5`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-steel-600 font-medium">{label}</p>
          <p className="text-3xl font-bold text-navy-900 mt-2">{value}</p>
        </div>
        <div className="text-4xl opacity-30">{icon}</div>
      </div>
    </div>
  )
}
