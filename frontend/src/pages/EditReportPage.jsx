import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save, AlertCircle } from 'lucide-react'
import { reportsAPI } from '../services/api'

export default function EditReportPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    reportsAPI.getReportDetail(id)
      .then(({ data }) => {
        const report = data.report
        setForm({
          report_text: report.report_text || '',
          report_type: report.report_type || 'near_miss',
          date: report.date ? report.date.slice(0, 10) : '',
          location: report.location || '',
          department: report.department || '',
          activity: report.activity || '',
        })
      })
      .catch(() => setError('Unable to load this report for editing.'))
      .finally(() => setIsLoading(false))
  }, [id])

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (form.report_text.trim().length < 10) {
      setError('Report description must be at least 10 characters.')
      return
    }
    setIsSaving(true)
    setError('')
    setSuccess('')
    try {
      await reportsAPI.updateReport(id, {
        ...form,
        report_text: form.report_text.trim(),
        date: form.date ? new Date(`${form.date}T00:00:00`).toISOString() : null,
        location: form.location || null,
        department: form.department || null,
        activity: form.activity || null,
      })
      setSuccess('Report information saved successfully.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save report changes.')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) return <div className="flex h-96 items-center justify-center"><div className="text-center"><span className="loading-spinner" /><p className="mt-3 text-steel-600">Loading report...</p></div></div>
  if (!form) return <div className="risk-high rounded-xl border p-6 text-center">{error}<button onClick={() => navigate('/reports')} className="btn btn-secondary mt-4">Back to reports</button></div>

  return (
    <div className="mx-auto max-w-4xl space-y-6 animate-fade-in">
      <button onClick={() => navigate(`/reports/${id}`)} className="flex items-center gap-2 font-semibold text-navy-700 hover:text-navy-900"><ArrowLeft size={18} /> Back to report</button>
      <header><p className="section-kicker mb-2">Report management</p><h1 className="text-3xl font-bold text-navy-900">Edit safety report</h1><p className="mt-2 text-steel-600">Update report information without changing the stored AI prediction.</p></header>
      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="bg-white rounded-xl p-6 shadow-card"><h2 className="mb-5 text-xl font-bold text-navy-900">Report information</h2><div className="grid gap-4 sm:grid-cols-2">
          <label>Report type<select value={form.report_type} onChange={(e) => updateField('report_type', e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2"><option value="near_miss">Near miss</option><option value="unsafe_act">Unsafe act</option><option value="unsafe_condition">Unsafe condition</option></select></label>
          <label>Date<input type="date" value={form.date} onChange={(e) => updateField('date', e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
          <label>Location<input value={form.location} onChange={(e) => updateField('location', e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
          <label>Department<input value={form.department} onChange={(e) => updateField('department', e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
          <label className="sm:col-span-2">Activity<input value={form.activity} onChange={(e) => updateField('activity', e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2" /></label>
        </div></section>
        <section className="bg-white rounded-xl p-6 shadow-card"><h2 className="mb-2 text-xl font-bold text-navy-900">Incident description</h2><p className="mb-4 text-sm text-steel-600">Describe the unsafe act, condition, or near miss observed.</p><textarea value={form.report_text} onChange={(e) => updateField('report_text', e.target.value)} className="min-h-56 w-full resize-y rounded-lg border p-4" required /><div className="mt-5 flex flex-wrap justify-end gap-3"><button type="button" onClick={() => navigate(`/reports/${id}`)} className="btn btn-secondary px-4 py-2">Cancel</button><button type="submit" disabled={isSaving} className="btn btn-primary flex items-center gap-2 px-5 py-2"><Save size={17} />{isSaving ? 'Saving...' : 'Save changes'}</button></div></section>
      </form>
      {error && <div className="risk-critical flex gap-3 rounded-xl border p-4"><AlertCircle size={19} /><p>{error}</p></div>}
      {success && <div className="risk-low rounded-xl border p-4" role="status">{success}</div>}
    </div>
  )
}
