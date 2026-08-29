import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { reportsAPI } from '../services/api'
import { Search, FileText, AlertTriangle, Plus, Pencil } from 'lucide-react'
import { formatDate, truncateText } from '../utils/helpers'

export default function ReportsPage() {
  const navigate = useNavigate()
  const [reports, setReports] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [sifFilter, setSifFilter] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [skip, setSkip] = useState(0)
  const [total, setTotal] = useState(0)
  const limit = 20
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  const canCreate = currentUser.role === 'employee'
  const canEdit = ['admin', 'safety_officer'].includes(currentUser.role)

  useEffect(() => {
    loadReports()
  }, [skip, sifFilter, riskFilter])

  const loadReports = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await reportsAPI.getReports(
        skip,
        limit,
        sifFilter || null,
        riskFilter || null
      )
      setReports(response.data.reports)
      setTotal(response.data.total)
    } catch (err) {
      setError('Failed to load reports')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchAndFilter = () => {
    if (skip !== 0) setSkip(0)
  }

  const filteredReports = reports.filter((report) =>
    report.report_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.department?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handlePageChange = (newSkip) => {
    setSkip(newSkip)
  }

  return (
    <div className="fade-in space-y-6">
      {/* Page Header */}
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
        <p className="section-kicker">Evidence register</p>
        <h1 className="page-title flex items-center gap-3">
          <FileText size={28} className="text-primary-600" />
          Safety reports
        </h1>
        <p className="page-subtitle mt-2">Review analyzed observations, prioritize risk, and open a report for validation.</p>
        </div>
        {canCreate && <button onClick={() => navigate('/reports/new')} className="btn btn-primary flex items-center gap-2 px-4 py-2"><Plus size={17} /> New safety report</button>}
      </div>

      {/* Search and Filter Section */}
      <div className="card space-y-4 p-5 sm:p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative col-span-1 md:col-span-2">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search by text, location, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* SIF Filter */}
          <select
            value={sifFilter}
            onChange={(e) => setSifFilter(e.target.value)}
          >
            <option value="">All SIF Status</option>
            <option value="YES">YES - Potential Precursor</option>
            <option value="NO">NO - Not Detected</option>
            <option value="UNCERTAIN">UNCERTAIN</option>
          </select>

          {/* Risk Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="">All Risk Levels</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>

        {/* Search Button */}
        <div className="flex gap-2">
          <button
            onClick={handleSearchAndFilter}
            className="btn btn-primary px-5 py-2.5 text-sm"
          >
            <Search size={18} />
            Search
          </button>
          <button
            onClick={() => {
              setSearchTerm('')
              setSifFilter('')
              setRiskFilter('')
              setSkip(0)
            }}
            className="btn btn-secondary px-4 py-2.5 text-sm"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {error && (
        <div className="risk-high flex gap-3 rounded-xl border p-4">
          <AlertTriangle size={20} className="flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Reports Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-steel-600">Loading reports...</p>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="p-12 text-center">
            <FileText size={48} className="mx-auto text-steel-300 mb-4" />
            <p className="text-steel-600 text-lg">No reports found</p>
            <p className="text-steel-500 text-sm mt-2">Try adjusting your search filters</p>
          </div>
        ) : (
          <>
            <div className="space-y-3 p-4 sm:hidden">
              {filteredReports.map((report) => (
                <ReportCard key={report.report_id} report={report} onViewDetail={() => navigate(`/reports/${report.report_id}`)} />
              ))}
            </div>
            <div className="overflow-x-auto">
              <table className="hidden w-full sm:table">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-600">Report text</th>
                    <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-600">Date</th>
                    <th className="px-6 py-3 text-center text-xs font-bold uppercase tracking-wider text-slate-600">SIF</th>
                    <th className="px-6 py-3 text-center text-xs font-bold uppercase tracking-wider text-slate-600">Risk</th>
                    <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-600">Location</th>
                    <th className="px-6 py-3 text-center text-xs font-bold uppercase tracking-wider text-slate-600">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReports.map((report, idx) => (
                    <ReportRow
                      key={report.report_id}
                      report={report}
                      onViewDetail={() => navigate(`/reports/${report.report_id}`)}
                      canEdit={canEdit}
                      onEdit={() => navigate(`/reports/${report.report_id}/edit`)}
                      isAlt={idx % 2 === 1}
                    />
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-4">
              <p className="text-sm text-slate-600">
                Showing {Math.min(skip + 1, total)} to {Math.min(skip + limit, total)} of {total} reports
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => handlePageChange(Math.max(0, skip - limit))}
                  disabled={skip === 0}
                  className="btn btn-secondary px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
                >
                  ← Previous
                </button>
                <button
                  onClick={() => handlePageChange(skip + limit)}
                  disabled={skip + limit >= total}
                  className="btn btn-secondary px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Next →
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function ReportRow({ report, onViewDetail, isAlt, canEdit, onEdit }) {
  return (
    <tr className={`border-b border-slate-200 ${isAlt ? 'bg-slate-50' : 'bg-white'} hover:bg-primary-50 transition`}>
      <td className="px-6 py-4 text-sm text-slate-700">
        {truncateText(report.report_text, 60)}
      </td>
      <td className="px-6 py-4 text-sm text-slate-600">
        {formatDate(report.created_at)}
      </td>
      <td className="px-6 py-4 text-center">
        <SIFBadge status={report.sif_status} />
      </td>
      <td className="px-6 py-4 text-center">
        <RiskBadge risk={report.risk_level} />
      </td>
      <td className="px-6 py-4 text-sm text-slate-600">
        {report.location || '—'}
      </td>
      <td className="px-6 py-4 text-center">
        <div className="flex items-center justify-center gap-2"><button onClick={onViewDetail} className="btn btn-secondary px-3 py-1.5 text-xs">View</button>{canEdit && <button onClick={onEdit} className="rounded-lg p-2 text-primary-700 hover:bg-primary-50" aria-label="Edit report"><Pencil size={15} /></button>}</div>
      </td>
    </tr>
  )
}

function ReportCard({ report, onViewDetail }) {
  return (
    <article className="card p-4">
      <div className="flex items-start justify-between gap-3">
        <div><p className="font-mono text-xs text-primary-600">#{report.report_id?.slice(0, 8)}</p><p className="mt-1 text-sm font-semibold text-slate-800">{report.location || 'Location not specified'}</p></div>
        <RiskBadge risk={report.risk_level} />
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-600">{truncateText(report.report_text, 120)}</p>
      <div className="mt-4 flex items-center justify-between gap-3 border-t border-slate-200 pt-3"><div className="flex items-center gap-2"><SIFBadge status={report.sif_status} /><span className="text-xs text-slate-500">{formatDate(report.created_at)}</span></div><button onClick={onViewDetail} className="btn btn-primary px-3 py-1.5 text-xs">Open report</button></div>
    </article>
  )
}

function SIFBadge({ status }) {
  if (!status) return <span className="text-steel-500">—</span>
  
  const colors = {
    YES: 'bg-green-100 text-green-900 border-green-300',
    NO: 'bg-blue-100 text-blue-900 border-blue-300',
    UNCERTAIN: 'bg-yellow-100 text-yellow-900 border-yellow-300',
  }
  
  return (
    <span className={`inline-block px-2 py-1 text-xs font-bold rounded border ${colors[status] || 'bg-steel-100 text-steel-900'}`}>
      {status}
    </span>
  )
}

function RiskBadge({ risk }) {
  if (!risk) return <span className="text-steel-500">—</span>
  
  const colors = {
    CRITICAL: 'bg-red-100 text-red-900 border-red-300',
    HIGH: 'bg-orange-100 text-orange-900 border-orange-300',
    MEDIUM: 'bg-blue-100 text-blue-900 border-blue-300',
    LOW: 'bg-green-100 text-green-900 border-green-300',
  }
  
  return (
    <span className={`inline-block px-2 py-1 text-xs font-bold rounded border ${colors[risk] || 'bg-steel-100 text-steel-900'}`}>
      {risk}
    </span>
  )
}
