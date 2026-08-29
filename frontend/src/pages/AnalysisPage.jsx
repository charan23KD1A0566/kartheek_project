import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analysisAPI, reportsAPI } from '../services/api'
import { AlertCircle, Brain, Check, X, Copy, ShieldAlert } from 'lucide-react'
import { getRiskBgColor, getRiskColor, getSIFStatusBgColor, getSIFStatusColor } from '../utils/helpers'

const DEMO_REPORT = "During maintenance, a worker entered an energized equipment area without completing the required isolation procedure."

export default function AnalysisPage() {
  const navigate = useNavigate()
  const [reportText, setReportText] = useState(DEMO_REPORT)
  const [analysis, setAnalysis] = useState(null)
  const [reportId, setReportId] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [validation, setValidation] = useState(null)
  const [isSavingValidation, setIsSavingValidation] = useState(false)
  const [validationSaved, setValidationSaved] = useState(false)
  const [modifiedSifStatus, setModifiedSifStatus] = useState('UNCERTAIN')
  const [modifiedRiskLevel, setModifiedRiskLevel] = useState('MEDIUM')
  const [comments, setComments] = useState('')
  const [reportType, setReportType] = useState('near_miss')
  const [location, setLocation] = useState('')
  const [department, setDepartment] = useState('')
  const [activity, setActivity] = useState('')
  const [reportDate, setReportDate] = useState('')
  const [showSafetyAlert, setShowSafetyAlert] = useState(false)
  const canValidate = ['admin', 'safety_officer'].includes(JSON.parse(localStorage.getItem('user') || '{}').role)

  const handleAnalyze = async () => {
    if (!reportText.trim()) {
      setError('Please enter a report to analyze')
      return
    }

    if (reportText.length < 10) {
      setError('Report must be at least 10 characters')
      return
    }

    setIsAnalyzing(true)
    setError('')
    setAnalysis(null)
    setValidation(null)

    try {
      const response = await analysisAPI.createAndAnalyze({
        report_text: reportText.trim(),
        report_type: reportType,
        location: location || null,
        department: department || null,
        activity: activity || null,
        date: reportDate ? new Date(`${reportDate}T00:00:00`).toISOString() : null,
      })
      setAnalysis(response.data.analysis)
      setReportId(response.data.report_id)
      if (response.data.analysis.risk_level === 'HIGH' || response.data.analysis.risk_level === 'CRITICAL') {
        setShowSafetyAlert(true)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
      console.error(err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  useEffect(() => {
    if (!showSafetyAlert) return undefined
    const timer = window.setTimeout(() => setShowSafetyAlert(false), 3000)
    return () => window.clearTimeout(timer)
  }, [showSafetyAlert])

  const handleValidation = async (decision) => {
    if (!reportId || !analysis) return

    setValidation(decision)
    setValidationSaved(false)
    if (decision === 'MODIFY') return

    await saveValidation(decision)
  }

  const saveValidation = async (decision) => {
    if (!reportId || !analysis) return

    setIsSavingValidation(true)
    setError('')
    try {
      await reportsAPI.validateReport(reportId, {
        ai_decision: analysis.sif_status,
        human_decision: decision,
        modified_sif_status: decision === 'MODIFY' ? modifiedSifStatus : null,
        modified_risk_level: decision === 'MODIFY' ? modifiedRiskLevel : null,
        comments: decision === 'MODIFY' ? comments.trim() : null,
      })
      setValidation(decision)
      setValidationSaved(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Validation could not be saved. Please try again.')
    } finally {
      setIsSavingValidation(false)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(reportText)
  }

  const handleUseDemoReport = () => {
    setReportText(DEMO_REPORT)
    setAnalysis(null)
    setReportId(null)
    setValidation(null)
    setError('')
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {showSafetyAlert && analysis && <div className="fixed right-4 top-4 z-50 w-[min(24rem,calc(100vw-2rem))] animate-fade-in rounded-2xl border border-red-300 bg-red-50 p-5 text-red-900 shadow-2xl" role="alert"><div className="flex items-start gap-3"><ShieldAlert className="mt-0.5 shrink-0 text-red-600" size={24} /><div><p className="text-xs font-bold uppercase tracking-widest text-red-700">Safety alert</p><p className="mt-1 font-bold">Potential SIF precursor detected</p><p className="mt-2 text-sm">Risk: {analysis.risk_level} · SIF probability: {Math.round(analysis.sif_probability * 100)}%</p><p className="mt-2 text-xs">Immediate safety review recommended.</p></div></div></div>}
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-navy-900 mb-2 flex items-center gap-3">
          <Brain size={32} className="text-amber-500" />
          AI Safety Report Analysis
        </h1>
        <p className="text-steel-600">
          Paste your workplace safety report and let our AI analyze it for SIF precursors
        </p>
      </div>

      {/* Important Disclaimer */}
      <div className="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-4 flex gap-3">
        <AlertCircle size={20} className="text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-900">
          <p className="font-semibold">⚠️ Prototype Decision Support System</p>
          <p className="mt-1">
            All AI results require review by qualified safety professionals. This system identifies potential
            SIF precursor patterns and prioritizes reports for expert review.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-4">
          {/* Report Input Card */}
          <div className="bg-white rounded-xl shadow-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-navy-900">Safety Report Text</h2>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 px-3 py-1 text-sm bg-steel-100 hover:bg-steel-200 rounded-lg text-steel-700 transition"
              >
                <Copy size={16} /> Copy
              </button>
            </div>

            <textarea
              value={reportText}
              onChange={(e) => setReportText(e.target.value)}
              placeholder="Paste your workplace safety report here..."
              className="w-full h-64 p-4 border-2 border-steel-200 rounded-lg focus:border-amber-500 focus:ring-2 focus:ring-amber-200 resize-none"
            />

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label>Report type<select value={reportType} onChange={(event) => setReportType(event.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2"><option value="near_miss">Near miss</option><option value="unsafe_act">Unsafe act</option><option value="unsafe_condition">Unsafe condition</option></select></label>
              <label>Date<input type="date" value={reportDate} onChange={(event) => setReportDate(event.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
              <label>Location<input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Worksite or area" className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
              <label>Department<input value={department} onChange={(event) => setDepartment(event.target.value)} placeholder="Owning department" className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
              <label className="sm:col-span-2">Activity<input value={activity} onChange={(event) => setActivity(event.target.value)} placeholder="Activity being observed" className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg font-bold transition ${
                  isAnalyzing
                    ? 'bg-steel-300 text-steel-600 cursor-not-allowed'
                    : 'bg-navy-700 text-white hover:bg-navy-900'
                }`}
              >
                <Brain size={20} />
                {isAnalyzing ? 'Analyzing...' : 'Analyze Report'}
              </button>
              <button
                onClick={handleUseDemoReport}
                className="px-4 py-3 border-2 border-navy-700 text-navy-700 rounded-lg font-bold hover:bg-navy-50 transition"
              >
                📝 Demo
              </button>
            </div>

            {error && (
              <div className="risk-critical rounded-lg p-4 mt-4 flex gap-3">
                <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Info Sidebar */}
        <div className="space-y-4">
          {/* Report Statistics */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
            <p className="text-sm font-semibold text-blue-900 mb-2">Report Statistics</p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-steel-600">Characters:</span>
                <span className="font-bold text-navy-900">{reportText.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-steel-600">Words:</span>
                <span className="font-bold text-navy-900">{reportText.trim().split(/\s+/).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-steel-600">Status:</span>
                <span className={`font-bold ${reportText.length >= 10 ? 'text-green-600' : 'text-red-600'}`}>
                  {reportText.length >= 10 ? '✓ Ready' : '✗ Too short'}
                </span>
              </div>
            </div>
          </div>

          {/* Demo Report Suggestion */}
          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-4">
            <p className="text-sm font-semibold text-yellow-900 mb-3">Try This Demo Report:</p>
            <p className="text-xs text-yellow-800 mb-3 italic">
              "{DEMO_REPORT}"
            </p>
            <button
              onClick={handleUseDemoReport}
              className="w-full py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-bold text-sm transition"
            >
              Load Demo Report
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Results */}
      {isAnalyzing && (
        <div className="glass-panel animate-slide-up rounded-2xl p-8 text-center"><div className="login-orbit mx-auto my-0 scale-75"><div className="orbit-ring orbit-ring-one"></div><div className="orbit-ring orbit-ring-two"></div><div className="orbit-core"><Brain size={30} /><span>SCANNING</span></div></div><p className="section-kicker mt-2">Deterministic analysis in progress</p><p className="mt-2 text-sm text-steel-400">Analyzing safety report...</p></div>
      )}

      {analysis && !isAnalyzing && (
        <div className="animate-slide-up space-y-6">
          <div className="bg-white rounded-xl shadow-card p-6 border-t-4" style={{ borderTopColor: getRiskColor(analysis.risk_level) }}>
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3"><div><p className="section-kicker">Analysis complete</p><h2 className="mt-1 text-2xl font-bold text-slate-900">AI safety assessment</h2></div><span className="badge badge-medium">{analysis.model_type} / v{analysis.model_version}</span></div>
            {/* Main Result Cards */}
            <div className="grid grid-cols-1 gap-4 mb-6 md:grid-cols-4">
              {/* SIF Status */}
              <div
                className="rounded-xl p-4"
                style={{ backgroundColor: getSIFStatusBgColor(analysis.sif_status) }}
              >
                <p className="text-sm font-semibold opacity-75 mb-1">SIF Precursor Status</p>
                <p
                  className="text-3xl font-bold"
                  style={{ color: getSIFStatusColor(analysis.sif_status) }}
                >
                  {analysis.sif_status}
                </p>
                <p className="text-xs opacity-60 mt-2">
                  {analysis.sif_status === 'YES'
                    ? 'Potential SIF precursor detected'
                    : analysis.sif_status === 'NO'
                    ? 'No SIF precursor indicators'
                    : 'Insufficient evidence for determination'}
                </p>
              </div>

              <div className="rounded-xl border-2 border-primary-200 bg-primary-50 p-4">
                <p className="mb-1 text-sm font-semibold text-primary-900">SIF Probability</p>
                <p className="text-3xl font-bold text-primary-600">{Math.round((analysis.sif_probability ?? 0.5) * 100)}%</p>
                <div className="mt-3 h-2 w-full rounded-full bg-primary-200"><div className="h-2 rounded-full bg-primary-600" style={{ width: `${Math.round((analysis.sif_probability ?? 0.5) * 100)}%` }} /></div>
              </div>

              {/* Confidence */}
              <div className="bg-blue-50 rounded-xl p-4 border-2 border-blue-200">
                <p className="text-sm font-semibold text-blue-900 mb-1">Confidence</p>
                <p className="text-3xl font-bold text-blue-600">{analysis.confidence}%</p>
                <div className="w-full bg-blue-200 rounded-full h-2 mt-3">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${analysis.confidence}%` }}
                  ></div>
                </div>
              </div>

              {/* Risk Level */}
              <div
                className="rounded-xl p-4"
                style={{ backgroundColor: getRiskBgColor(analysis.risk_level) }}
              >
                <p className="text-sm font-semibold opacity-75 mb-1">Risk Level</p>
                <p
                  className="text-3xl font-bold"
                  style={{ color: getRiskColor(analysis.risk_level) }}
                >
                  {analysis.risk_level}
                </p>
              </div>
            </div>

            {/* Detected Hazards */}
            <div className="mb-6">
              <h3 className="text-lg font-bold text-navy-900 mb-3">🚨 Detected Hazards</h3>
              {(analysis.hazards || []).length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {(analysis.hazards || []).map((hazard, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-amber-100 text-amber-900 rounded-full text-sm font-semibold border border-amber-300"
                    >
                      {hazard}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-steel-600">No hazards detected</p>
              )}
            </div>

            {/* Exposure */}
            <div className="mb-6">
              <h3 className="text-lg font-bold text-navy-900 mb-3">👤 Worker Exposure</h3>
              {(analysis.exposure || []).length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {(analysis.exposure || []).map((exp, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-orange-100 text-orange-900 rounded-full text-sm font-semibold border border-orange-300"
                    >
                      {exp}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-steel-600">No specific exposure detected</p>
              )}
            </div>

            {/* Control Failures */}
            <div className="mb-6">
              <h3 className="text-lg font-bold text-navy-900 mb-3">⚠️ Control Failures</h3>
              {(analysis.control_failures || []).length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {(analysis.control_failures || []).map((cf, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-red-100 text-red-900 rounded-full text-sm font-semibold border border-red-300"
                    >
                      {cf}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-steel-600">No control failures detected</p>
              )}
            </div>

            {/* Evidence */}
            <div className="mb-6">
              <h3 className="text-lg font-bold text-navy-900 mb-3">📋 Extracted Evidence</h3>
              {(analysis.evidence || []).length > 0 ? (
                <div className="space-y-2">
                  {(analysis.evidence || []).map((ev, idx) => (
                    <div key={idx} className="bg-steel-50 p-3 rounded-lg border-l-4 border-amber-500">
                      <p className="text-sm text-navy-700">"{ev}"</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-steel-600">No specific evidence extracted</p>
              )}
            </div>

            {/* Explanation */}
            <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-blue-900 mb-2">💡 AI Explanation</h3>
              <p className="text-blue-800">{analysis.explanation}</p>
            </div>

            {/* Recommendation */}
            <div className="mb-6 bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-green-900 mb-2">✓ Recommendation</h3>
              <p className="text-green-800 whitespace-pre-wrap">{analysis.recommendation}</p>
            </div>

            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4">
              <h3 className="text-lg font-bold text-red-900">Safety action plan</h3>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {Object.entries(analysis.safety_action_plan || {}).map(([section, actions]) => <div key={section}><p className="text-sm font-bold text-red-800">{section}</p><ul className="mt-2 space-y-1 text-sm text-red-900">{actions.map((action) => <li key={action} className="flex gap-2"><span aria-hidden="true">•</span><span>{action}</span></li>)}</ul></div>)}
              </div>
            </div>

            {/* Model Info */}
            <div className="text-xs text-steel-600 flex justify-between pt-4 border-t border-steel-200">
              <span>Model: {analysis.model_type} v{analysis.model_version}</span>
              <span>Probability from the persisted model; taxonomy provides evidence</span>
            </div>
          </div>

          {/* Validation Section */}
          {canValidate && <div className="bg-white rounded-xl shadow-card p-6">
            <h3 className="text-lg font-bold text-navy-900 mb-4">✅ Validate Analysis</h3>
            <p className="text-sm text-steel-600 mb-4">
              Do you agree with this AI analysis?
            </p>

            <div className="grid grid-cols-3 gap-3 mb-4">
              <button
                onClick={() => handleValidation('AGREE')}
                disabled={isSavingValidation}
                className={`py-3 rounded-lg font-bold transition ${
                  validation === 'AGREE'
                    ? 'bg-green-500 text-white ring-2 ring-green-300'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                <Check size={20} className="mx-auto mb-1" />
                Agree
              </button>
              <button
                onClick={() => handleValidation('DISAGREE')}
                disabled={isSavingValidation}
                className={`py-3 rounded-lg font-bold transition ${
                  validation === 'DISAGREE'
                    ? 'bg-red-500 text-white ring-2 ring-red-300'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                }`}
              >
                <X size={20} className="mx-auto mb-1" />
                Disagree
              </button>
              <button
                onClick={() => handleValidation('MODIFY')}
                disabled={isSavingValidation}
                className={`py-3 rounded-lg font-bold transition ${
                  validation === 'MODIFY'
                    ? 'bg-amber-500 text-white ring-2 ring-amber-300'
                    : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                }`}
              >
                ✏️ Modify
              </button>
            </div>

            {validation && (
              <div className="space-y-3">
                {validation === 'MODIFY' && (
                  <div className="grid gap-3 sm:grid-cols-2">
                    <label className="text-sm font-semibold text-navy-900">
                      Modified SIF status
                      <select
                        value={modifiedSifStatus}
                        onChange={(event) => setModifiedSifStatus(event.target.value)}
                        className="mt-1 w-full rounded-lg border border-steel-300 px-3 py-2 font-normal"
                      >
                        <option value="YES">YES</option>
                        <option value="NO">NO</option>
                        <option value="UNCERTAIN">UNCERTAIN</option>
                      </select>
                    </label>
                    <label className="text-sm font-semibold text-navy-900">
                      Modified risk level
                      <select
                        value={modifiedRiskLevel}
                        onChange={(event) => setModifiedRiskLevel(event.target.value)}
                        className="mt-1 w-full rounded-lg border border-steel-300 px-3 py-2 font-normal"
                      >
                        <option value="LOW">LOW</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="HIGH">HIGH</option>
                        <option value="CRITICAL">CRITICAL</option>
                      </select>
                    </label>
                    <label className="text-sm font-semibold text-navy-900 sm:col-span-2">
                      Reviewer comments
                      <textarea
                        value={comments}
                        onChange={(event) => setComments(event.target.value)}
                        placeholder="Explain why the AI result should be changed"
                        className="mt-1 h-20 w-full rounded-lg border border-steel-300 px-3 py-2 font-normal"
                      />
                    </label>
                    <button
                      onClick={() => saveValidation('MODIFY')}
                      disabled={isSavingValidation || !comments.trim()}
                      className="sm:col-span-2 w-full rounded-lg bg-navy-700 py-3 font-bold text-white transition hover:bg-navy-900 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {isSavingValidation ? 'Saving...' : 'Save Modified Validation'}
                    </button>
                  </div>
                )}
                {validation !== 'MODIFY' && (
                  <p className="text-sm font-semibold text-green-700">Validation saved for report {reportId?.slice(0, 8)}.</p>
                )}
                {validation === 'MODIFY' && validationSaved && (
                  <p className="text-sm font-semibold text-green-700">Modified validation saved for report {reportId?.slice(0, 8)}.</p>
                )}
                <button
                  onClick={() => navigate(`/reports/${reportId}`)}
                  disabled={isSavingValidation || (validation === 'MODIFY' && !validationSaved)}
                  className="w-full py-3 bg-navy-700 text-white rounded-lg font-bold hover:bg-navy-900 transition"
                >
                  View Saved Report
                </button>
              </div>
            )}
          </div>}
        </div>
      )}
    </div>
  )
}
