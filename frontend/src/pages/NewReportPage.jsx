import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowLeft, CheckCircle2, Loader2, ShieldCheck } from 'lucide-react'
import { analysisAPI } from '../services/api'

const initialForm = {
  report_text: '',
  report_type: 'near_miss',
  location: '',
  department: '',
  activity: '',
  date: '',
}

export default function NewReportPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const charCount = useMemo(() => form.report_text.length, [form.report_text])

  const updateField = (field, value) => setForm((previous) => ({ ...previous, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!form.report_text.trim()) {
      setError('Describe the incident before submitting the report.')
      return
    }

    if (form.report_text.trim().length < 10) {
      setError('Report description must be at least 10 characters long.')
      return
    }

    setError('')
    setIsSubmitting(true)

    try {
      const response = await analysisAPI.createAndAnalyze({
        report_text: form.report_text.trim(),
        report_type: form.report_type,
        location: form.location || null,
        department: form.department || null,
        activity: form.activity || null,
        date: form.date ? new Date(`${form.date}T00:00:00`).toISOString() : null,
      })

      const reportId = response.data.report_id
      navigate(`/reports/${reportId}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to create and analyze the report. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fade-in space-y-6">
      <button type="button" onClick={() => navigate('/reports')} className="btn btn-secondary px-3.5 py-2.5 text-sm">
        <ArrowLeft size={16} className="mr-2" /> Back to reports
      </button>

      <header>
        <p className="section-kicker">Report intake</p>
        <h1 className="page-title">New safety report</h1>
        <p className="page-subtitle mt-2">Capture working conditions, unsafe actions, or near misses for AI-assisted review.</p>
      </header>

      <form onSubmit={handleSubmit} className="card p-5 sm:p-6 lg:p-7">
        <div className="grid gap-5 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Report type</label>
            <select value={form.report_type} onChange={(event) => updateField('report_type', event.target.value)}>
              <option value="near_miss">Near miss</option>
              <option value="unsafe_act">Unsafe act</option>
              <option value="unsafe_condition">Unsafe condition</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Date</label>
            <input type="date" value={form.date} onChange={(event) => updateField('date', event.target.value)} />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Location</label>
            <input value={form.location} onChange={(event) => updateField('location', event.target.value)} placeholder="Workshop A, Offshore platform..." />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Department</label>
            <input value={form.department} onChange={(event) => updateField('department', event.target.value)} placeholder="Maintenance, Drilling..." />
          </div>

          <div className="md:col-span-2">
            <label className="mb-2 block text-sm font-semibold text-slate-700">Activity</label>
            <input value={form.activity} onChange={(event) => updateField('activity', event.target.value)} placeholder="Equipment inspection, lifting..." />
          </div>

          <div className="md:col-span-2">
            <div className="mb-2 flex items-center justify-between">
              <label className="block text-sm font-semibold text-slate-700">Report description</label>
              <span className={`text-xs font-semibold ${charCount >= 10 ? 'text-emerald-600' : 'text-slate-500'}`}>
                {charCount} characters
              </span>
            </div>

            <textarea
              rows={8}
              value={form.report_text}
              onChange={(event) => updateField('report_text', event.target.value)}
              placeholder="Describe the unsafe act, unsafe condition or near miss..."
            />
          </div>
        </div>

        {error && (
          <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            <AlertCircle size={18} className="mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-5">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <ShieldCheck size={16} className="text-emerald-600" />
            AI analysis will be generated after submission.
          </div>

          <button type="submit" disabled={isSubmitting} className="btn btn-primary px-5 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-70">
            {isSubmitting ? (
              <>
                <Loader2 size={16} className="mr-2 animate-spin" />
                Analyzing report...
              </>
            ) : (
              <>
                <CheckCircle2 size={16} className="mr-2" />
                Analyze & save report
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
