import { useEffect, useState } from 'react'
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { dashboardAPI, analyticsAPI } from '../services/api'
import { TrendingUp, AlertTriangle, CheckCircle, Clock, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    setError('')
    try {
      const [dashboardRes, analyticsRes] = await Promise.all([
        dashboardAPI.getStats(),
        analyticsAPI.getAnalytics(),
      ])
      setStats(dashboardRes.data.stats)
      setAnalytics(analyticsRes.data)
    } catch (err) {
      setError('Failed to load dashboard data')
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
          <p className="text-steel-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="risk-high rounded-lg p-6 text-center">
        <p className="font-semibold">{error}</p>
        <button
          onClick={loadData}
          className="btn btn-secondary mt-4"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!stats || !analytics) {
    return <div className="card p-10 text-center text-slate-500">No data available</div>
  }

  const riskData = [
    { name: 'Critical', value: analytics.risk_distribution?.CRITICAL || 0, fill: '#ef4444' },
    { name: 'High', value: analytics.risk_distribution?.HIGH || 0, fill: '#f59e0b' },
    { name: 'Medium', value: analytics.risk_distribution?.MEDIUM || 0, fill: '#3b82f6' },
    { name: 'Low', value: analytics.risk_distribution?.LOW || 0, fill: '#22c55e' },
  ].filter(d => d.value > 0)

  return (
    <div className="fade-in space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="section-kicker">Operations overview</p>
          <h1 className="page-title">Safety intelligence dashboard</h1>
          <p className="page-subtitle mt-2">Live monitoring of analyzed reports, risk signals, and review workload.</p>
        </div>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-bold uppercase tracking-[0.12em] text-emerald-700">Live data</div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Reports */}
        <KPICard
          icon={<TrendingUp className="text-blue-500" size={28} />}
          label="Total Reports"
          value={stats.total_reports}
          color="blue"
        />

        {/* SIF Precursors */}
        <KPICard
          icon={<AlertTriangle className="text-amber-500" size={28} />}
          label="Potential SIF"
          value={stats.potential_sif_precursors}
          subtext={stats.total_reports > 0 ? `${((stats.potential_sif_precursors / stats.total_reports) * 100).toFixed(1)}% of reports` : '0%'}
          color="amber"
        />

        {/* Critical Risk */}
        <KPICard
          icon={<AlertCircle className="text-red-500" size={28} />}
          label="Critical Risk"
          value={stats.critical_risk_reports}
          color="red"
          highlight={true}
        />

        {/* Pending Validation */}
        <KPICard
          icon={<Clock className="text-steel-500" size={28} />}
          label="Pending Review"
          value={stats.pending_validation}
          color="steel"
        />
      </div>

      {/* Additional KPI Row */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* High Risk */}
        <KPICard
          icon={<AlertTriangle className="text-orange-500" size={24} />}
          label="High Risk Reports"
          value={stats.high_risk_reports}
          color="orange"
          size="small"
        />

        {/* Validated */}
        <KPICard
          icon={<CheckCircle className="text-green-500" size={24} />}
          label="Validated Reports"
          value={stats.validated_reports}
          color="green"
          size="small"
        />

        {/* Validation Agreement */}
        <KPICard
          icon={<TrendingUp className="text-teal-500" size={24} />}
          label="Agreement Rate"
          value={`${stats.validation_agreement_rate.toFixed(1)}%`}
          color="teal"
          size="small"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Risk Distribution */}
        <div className="card p-5 sm:p-6">
          <h3 className="text-lg font-bold text-slate-900">Risk distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Reports Over Time */}
        <div className="card p-5 sm:p-6">
          <h3 className="text-lg font-bold text-slate-900">Reports over time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.reports_over_time || []}>
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
              <Line
                type="monotone"
                dataKey="count"
                stroke="#1e3a5f"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hazards and Data Sources */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Hazards */}
        <div className="card p-5 sm:p-6">
          <h3 className="text-lg font-bold text-slate-900">Top detected hazards</h3>
          <div className="space-y-2">
            {(analytics.hazard_distribution || []).slice(0, 8).map((hazard, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm font-medium text-navy-700">{hazard.hazard}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-steel-200 rounded-full h-2">
                    <div
                      className="bg-amber-500 h-2 rounded-full"
                      style={{ width: `${Math.min(100, (hazard.count / (analytics.hazard_distribution[0]?.count || 1)) * 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-steel-600 w-8 text-right">{hazard.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Sources */}
        <div className="card p-5 sm:p-6">
          <h3 className="text-lg font-bold text-slate-900">Data source distribution</h3>
          <div className="space-y-3">
            {Object.entries(analytics.data_source_distribution || {}).map(([source, count]) => (
              <div key={source} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3">
                <span className="font-medium text-slate-700">{source}</span>
                <div className="flex items-center gap-2">
                  <span className="badge badge-medium">{count}</span>
                  <span className="text-xs text-steel-600 w-12 text-right">
                    {((count / stats.total_reports) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Important Notes */}
      <div className="rounded-xl border border-primary-200 bg-primary-50 p-4">
        <p className="text-sm text-primary-700">
          <strong>Review note:</strong> AI analysis is decision support. Safety professionals should validate high-consequence signals before action is taken.
        </p>
      </div>
    </div>
  )
}

function KPICard({ icon, label, value, subtext, color = 'navy', trend, highlight = false, size = 'default' }) {
  const colors = {
    navy: 'bg-slate-50 border-slate-200',
    blue: 'bg-primary-50 border-primary-200',
    amber: 'bg-amber-50 border-amber-200',
    red: 'bg-red-50 border-red-200',
    green: 'bg-emerald-50 border-emerald-200',
    orange: 'bg-orange-50 border-orange-200',
    steel: 'bg-slate-50 border-slate-200',
    teal: 'bg-teal-50 border-teal-200',
  }

  return (
    <div className={`card ${colors[color]} border-2 p-5 ${highlight ? 'ring-2 ring-red-300/50' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-600">{label}</p>
          {size === 'default' ? (
            <p className="mt-2 text-4xl font-black text-slate-900">{value}</p>
          ) : (
            <p className="mt-1 text-2xl font-black text-slate-900">{value}</p>
          )}
          {subtext && <p className="text-xs text-steel-500 mt-1">{subtext}</p>}
        </div>
        <div className="text-2xl opacity-70">{icon}</div>
      </div>
      {trend && <p className="text-xs text-green-600 font-semibold">{trend}</p>}
    </div>
  )
}
