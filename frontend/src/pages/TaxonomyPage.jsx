import { useEffect, useState } from 'react'
import { ChevronDown, Network, AlertTriangle } from 'lucide-react'
import { taxonomyAPI } from '../services/api'

export default function TaxonomyPage() {
  const [taxonomy, setTaxonomy] = useState(null)
  const [openCategory, setOpenCategory] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    taxonomyAPI.getTaxonomy()
      .then((response) => setTaxonomy(response.data))
      .catch(() => setError('Unable to load the SIF taxonomy.'))
      .finally(() => setIsLoading(false))
  }, [])

  if (isLoading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />

  const categories = Object.entries(taxonomy?.categories || {})
  const patterns = taxonomy?.patterns || []

  return (
    <div className="fade-in space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="section-kicker mb-2">SIF taxonomy intelligence</p>
          <h1 className="page-title">Precursor knowledge base</h1>
          <p className="page-subtitle mt-2 max-w-2xl">The live classification vocabulary used by the deterministic safety analysis engine.</p>
        </div>
        <div className="card px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-widest text-slate-500">Version</p>
          <p className="font-mono text-lg font-bold text-primary-700">v{taxonomy?.version || '—'}</p>
        </div>
      </header>

      <section className="grid gap-4 sm:grid-cols-3">
        <Metric label="Categories" value={categories.length} />
        <Metric label="Precursor patterns" value={patterns.length} />
        <Metric label="Engine" value="RULE" />
      </section>

      <section className="card p-5 sm:p-6">
        <div className="mb-5 flex items-center gap-3">
          <Network className="text-primary-600" size={20} />
          <div><h2 className="text-lg font-bold text-slate-900">Hazard classifications</h2><p className="text-xs text-slate-500">Expand a category to inspect its controls and keyword vocabulary.</p></div>
        </div>
        <div className="space-y-3">
          {categories.map(([key, category]) => {
            const isOpen = openCategory === key
            return (
              <div key={key} className="overflow-hidden rounded-xl border border-slate-200 bg-white">
                <button onClick={() => setOpenCategory(isOpen ? null : key)} className="flex w-full items-center justify-between gap-4 px-4 py-4 text-left transition hover:bg-primary-50" aria-expanded={isOpen}>
                  <div><p className="font-bold text-slate-900">{category.name}</p><p className="mt-1 text-sm text-slate-500">{category.description}</p></div>
                  <ChevronDown size={18} className={`shrink-0 text-primary-600 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </button>
                {isOpen && <div className="grid gap-5 border-t border-slate-200 px-4 py-4 md:grid-cols-2">
                  <div><p className="mb-2 text-xs font-bold uppercase tracking-widest text-primary-600">Subcategories</p><div className="flex flex-wrap gap-2">{(category.subcategories || []).map((item) => <span key={item} className="badge badge-medium">{item}</span>)}</div></div>
                  <div><p className="mb-2 text-xs font-bold uppercase tracking-widest text-amber-600">Detection vocabulary</p><div className="flex flex-wrap gap-2">{(category.keywords || []).map((item) => <span key={item} className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-xs text-slate-600">{item}</span>)}</div></div>
                </div>}
              </div>
            )
          })}
        </div>
      </section>

      <section className="card p-5 sm:p-6">
        <div className="mb-5 flex items-center gap-3"><AlertTriangle className="text-amber-600" size={20} /><div><h2 className="text-lg font-bold text-slate-900">Precursor patterns</h2><p className="text-xs text-slate-500">Pattern rules currently available to the analysis engine.</p></div></div>
        <div className="grid gap-3 md:grid-cols-2">{patterns.map((pattern) => <div key={pattern.pattern_id} className="rounded-xl border border-slate-200 bg-slate-50 p-4"><p className="font-bold text-slate-900">{pattern.name}</p><p className="mt-1 font-mono text-xs text-primary-600">{pattern.pattern_id}</p><p className="mt-3 text-sm text-slate-500">Hazard: <span className="text-slate-700">{pattern.hazard}</span></p></div>)}</div>
      </section>
    </div>
  )
}

function Metric({ label, value }) { return <div className="card p-4"><p className="text-xs uppercase tracking-widest text-slate-500">{label}</p><p className="mt-2 font-mono text-2xl font-bold text-primary-700">{value}</p></div> }
function LoadingState() { return <div className="flex h-96 items-center justify-center"><div className="text-center"><span className="loading-spinner" /><p className="mt-4 text-slate-500">Loading taxonomy intelligence...</p></div></div> }
function ErrorState({ message, onRetry }) { return <div className="risk-high rounded-xl border p-6 text-center"><p className="font-semibold">{message}</p><button onClick={onRetry} className="btn btn-secondary mt-4">Retry connection</button></div> }
