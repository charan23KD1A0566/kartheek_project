import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { reportsAPI } from '../services/api'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import { formatDate } from '../utils/helpers'

export default function ReportDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [validation, setValidation] = useState(null)
  const [isValidating, setIsValidating] = useState(false)
  const [selectedDecision, setSelectedDecision] = useState(null)
  const [modifiedSifStatus, setModifiedSifStatus] = useState('UNCERTAIN')
  const [modifiedRiskLevel, setModifiedRiskLevel] = useState('MEDIUM')
  const [comments, setComments] = useState('')
  const canValidate = ['admin', 'safety_officer'].includes(JSON.parse(localStorage.getItem('user') || '{}').role)

  useEffect(() => {
    loadReport()
  }, [id])

  const loadReport = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await reportsAPI.getReportDetail(id)
      setData(response.data)
      setValidation(response.data.validation)
    } catch (err) {
      setError('Failed to load report')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleValidate = async (decision) => {
    setSelectedDecision(decision)
    if (decision === 'MODIFY') return
    await saveValidation(decision)
  }

  const saveValidation = async (decision) => {
    setIsValidating(true)
    try {
      await reportsAPI.validateReport(id, {
        ai_decision: data.prediction?.sif_status,
        human_decision: decision,
        modified_sif_status: decision === 'MODIFY' ? modifiedSifStatus : null,
        modified_risk_level: decision === 'MODIFY' ? modifiedRiskLevel : null,
        comments: decision === 'MODIFY' ? comments.trim() : null,
      })
      await loadReport()
      alert('Validation saved successfully!')
    } catch (err) {
      alert('Failed to save validation: ' + err.message)
    } finally {
      setIsValidating(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-steel-600">Loading report...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="risk-high rounded-lg p-6 text-center">
        <p className="font-semibold">{error || 'Report not found'}</p>
        <button
          onClick={() => navigate('/reports')}
          className="btn btn-secondary mt-4"
        >
          Back to Reports
        </button>
      </div>
    )
  }

  const report = data.report
  const prediction = data.prediction
  const humanValidation = data.validation

  return (
    <div className="fade-in space-y-6">
      {/* Header */}
      <button
        onClick={() => navigate('/reports')}
        className="btn btn-secondary px-3.5 py-2.5 text-sm"
      >
        <ArrowLeft size={20} /> Back to Reports
      </button>

      {/* Report Card */}
      <div className="card p-5 sm:p-6">
        <div className="mb-6 pb-6 border-b border-steel-200">
          <h1 className="text-2xl font-black text-slate-900">Report #{report.report_id.slice(0, 8)}</h1>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-steel-600 font-semibold">Date</p>
              <p className="text-navy-900">{formatDate(report.created_at)}</p>
            </div>
            <div>
              <p className="text-steel-600 font-semibold">Location</p>
              <p className="text-navy-900">{report.location || '—'}</p>
            </div>
            <div>
              <p className="text-steel-600 font-semibold">Department</p>
              <p className="text-navy-900">{report.department || '—'}</p>
            </div>
            <div>
              <p className="text-steel-600 font-semibold">Data Source</p>
              <p className="text-navy-900">{report.data_source}</p>
            </div>
          </div>
        </div>

        {/* Report Text */}
        <div className="mb-6">
          <h2 className="text-lg font-bold text-navy-900 mb-3">Report Text</h2>
          <div className="rounded-xl border border-primary-200 bg-primary-50 p-4 leading-relaxed text-slate-700">
            {report.report_text}
          </div>
        </div>
      </div>

      {/* AI Analysis */}
      {prediction && (
        <div className="card border-t-4 border-primary-500 p-5 sm:p-6">
          <h2 className="text-2xl font-black text-slate-900">AI analysis results</h2>

          {/* Result Cards */}
          <div className="grid grid-cols-1 gap-4 mb-6 md:grid-cols-4">
            <ResultCard label="SIF Status" value={prediction.sif_status} type="sif" />
            <ResultCard label="SIF Probability" value={`${Math.round((prediction.sif_probability ?? 0.5) * 100)}%`} type="confidence" />
            <ResultCard label="Confidence" value={`${prediction.confidence}%`} type="confidence" />
            <ResultCard label="Risk Level" value={prediction.risk_level} type="risk" />
          </div>

          {/* Detected Issues */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <h3 className="font-bold text-navy-900 mb-2">Hazards</h3>
              {(prediction.hazards || []).length > 0 ? (
                <div className="space-y-1">
                  {(prediction.hazards || []).map((h, i) => (
                    <div key={i} className="text-sm bg-amber-50 p-2 rounded border border-amber-200 text-amber-900">
                      • {h}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-steel-500 text-sm">None detected</p>
              )}
            </div>

            <div>
              <h3 className="font-bold text-navy-900 mb-2">Exposure</h3>
              {(prediction.exposure || []).length > 0 ? (
                <div className="space-y-1">
                  {(prediction.exposure || []).map((e, i) => (
                    <div key={i} className="text-sm bg-orange-50 p-2 rounded border border-orange-200 text-orange-900">
                      • {e}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-steel-500 text-sm">None detected</p>
              )}
            </div>
          </div>

          {/* Control Failures */}
          <div className="mb-6">
            <h3 className="font-bold text-navy-900 mb-2">Control Failures</h3>
            {(prediction.control_failures || []).length > 0 ? (
              <div className="space-y-1">
                {(prediction.control_failures || []).map((cf, i) => (
                  <div key={i} className="text-sm bg-red-50 p-2 rounded border border-red-200 text-red-900">
                    • {cf}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-steel-500 text-sm">None detected</p>
            )}
          </div>

          {/* Explanation */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-6">
            <h3 className="font-bold text-blue-900 mb-2">Explanation</h3>
            <p className="text-blue-800 text-sm">{prediction.explanation}</p>
          </div>

          {/* Recommendation */}
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded mb-6">
            <h3 className="font-bold text-green-900 mb-2">Recommendation</h3>
            <p className="text-green-800 text-sm whitespace-pre-wrap">{prediction.recommendation}</p>
          </div>

          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4">
            <h3 className="text-lg font-bold text-red-900">Safety action plan</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {Object.entries(prediction.safety_action_plan || {}).map(([section, actions]) => <div key={section}><p className="text-sm font-bold text-red-800">{section}</p><ul className="mt-2 space-y-1 text-sm text-red-900">{actions.map((action) => <li key={action} className="flex gap-2"><span aria-hidden="true">•</span><span>{action}</span></li>)}</ul></div>)}
            </div>
          </div>

          {/* Model Info */}
          <div className="text-xs text-steel-600 flex justify-between pt-4 border-t border-steel-200">
            <span>Model: {prediction.model_type} v{prediction.model_version}</span>
            <span>Analyzed: {formatDate(prediction.created_at)}</span>
          </div>
        </div>
      )}

      {/* Human Validation */}
      <div className="card p-5 sm:p-6">
        <h2 className="text-xl font-black text-slate-900">Human validation</h2>

        {humanValidation ? (
          <div className="space-y-3">
            <div>
              <p className="text-sm text-steel-600 font-semibold">Human Decision</p>
              <p className="text-lg font-bold text-navy-900 capitalize">
                {humanValidation.human_decision}
              </p>
            </div>
            <div>
              <p className="text-sm text-steel-600 font-semibold">Reviewer</p>
              <p className="text-navy-900">{humanValidation.reviewer}</p>
            </div>
            <div>
              <p className="text-sm text-steel-600 font-semibold">Validation Date</p>
              <p className="text-navy-900">{formatDate(humanValidation.timestamp)}</p>
            </div>
            {humanValidation.comments && (
              <div>
                <p className="text-sm text-steel-600 font-semibold">Comments</p>
                <p className="text-navy-900">{humanValidation.comments}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-amber-50 border border-amber-200 rounded p-4 mb-4">
            <p className="text-amber-900 text-sm">This report has not been validated yet.</p>
          </div>
        )}

        {!humanValidation && canValidate && (
          <div className="mt-6 space-y-4">
            <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => handleValidate('AGREE')}
              disabled={isValidating}
              className="btn w-full bg-emerald-600 py-3 text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              👍 Agree
            </button>
            <button
              onClick={() => handleValidate('DISAGREE')}
              disabled={isValidating}
              className="btn w-full bg-red-600 py-3 text-white hover:bg-red-700 disabled:opacity-50"
            >
              👎 Disagree
            </button>
            <button
              onClick={() => handleValidate('MODIFY')}
              disabled={isValidating}
              className="btn w-full bg-amber-500 py-3 text-white hover:bg-amber-600 disabled:opacity-50"
            >
              ✏️ Modify
            </button>
            </div>
            {selectedDecision === 'MODIFY' && (
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="text-sm font-semibold text-navy-900">
                  Modified SIF status
                  <select value={modifiedSifStatus} onChange={(event) => setModifiedSifStatus(event.target.value)} className="mt-1 w-full rounded-lg border border-steel-300 px-3 py-2 font-normal">
                    <option value="YES">YES</option>
                    <option value="NO">NO</option>
                    <option value="UNCERTAIN">UNCERTAIN</option>
                  </select>
                </label>
                <label className="text-sm font-semibold text-navy-900">
                  Modified risk level
                  <select value={modifiedRiskLevel} onChange={(event) => setModifiedRiskLevel(event.target.value)} className="mt-1 w-full rounded-lg border border-steel-300 px-3 py-2 font-normal">
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </label>
                <label className="text-sm font-semibold text-navy-900 sm:col-span-2">
                  Reviewer comments
                  <textarea value={comments} onChange={(event) => setComments(event.target.value)} placeholder="Explain why the AI result should be changed" className="mt-1 h-20 w-full rounded-lg border border-steel-300 px-3 py-2 font-normal" />
                </label>
                <button onClick={() => saveValidation('MODIFY')} disabled={isValidating || !comments.trim()} className="btn btn-primary sm:col-span-2 py-3 disabled:cursor-not-allowed disabled:opacity-50">
                  {isValidating ? 'Saving...' : 'Save Modified Validation'}
                </button>
              </div>
            )}
          </div>
        )}
        {!humanValidation && !canValidate && (
          <p className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">Validation is restricted to administrators and safety officers.</p>
        )}
      </div>
    </div>
  )
}

function ResultCard({ label, value, type }) {
  const getStyle = () => {
    if (type === 'sif') {
      if (value === 'YES') return 'bg-green-50 border-green-200 text-green-900'
      if (value === 'NO') return 'bg-blue-50 border-blue-200 text-blue-900'
      return 'bg-yellow-50 border-yellow-200 text-yellow-900'
    }
    if (type === 'confidence') return 'bg-blue-50 border-blue-200 text-blue-900'
    if (type === 'risk') {
      if (value === 'CRITICAL') return 'bg-red-50 border-red-200 text-red-900'
      if (value === 'HIGH') return 'bg-orange-50 border-orange-200 text-orange-900'
      if (value === 'MEDIUM') return 'bg-blue-50 border-blue-200 text-blue-900'
      return 'bg-green-50 border-green-200 text-green-900'
    }
  }

  return (
    <div className={`border rounded-lg p-4 ${getStyle()}`}>
      <p className="text-sm font-semibold opacity-75 mb-1">{label}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  )
}
