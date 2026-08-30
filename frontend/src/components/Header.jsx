import { Bell, ExternalLink, Menu, Radio, ShieldCheck } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuthStore } from '../stores/appStore'
import { alertsAPI } from '../services/api'

const pageNames = {
  '/': 'Safety intelligence overview',
  '/analysis': 'AI safety analysis',
  '/reports/new': 'New safety report',
  '/reports': 'Safety reports',
  '/analytics': 'Operational analytics',
  '/taxonomy': 'Taxonomy intelligence',
}

export default function Header({ onMenuOpen }) {
  const { user } = useAuthStore()
  const location = useLocation()
  const [alerts, setAlerts] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const canSeeAlerts = ['MANAGER', 'SAFETY_OFFICER'].includes(user?.role)

  useEffect(() => {
    if (!canSeeAlerts) return undefined
    const loadUnread = () => alertsAPI.getUnread().then((response) => setAlerts(response.data.alerts || [])).catch(() => {})
    loadUnread()
    const timer = window.setInterval(loadUnread, 15000)
    return () => window.clearInterval(timer)
  }, [canSeeAlerts])

  const markRead = async (alertId) => {
    try {
      await alertsAPI.markRead(alertId)
      setAlerts((current) => current.filter((alert) => alert.alert_id !== alertId))
    } catch { }
  }

  const getPageTitle = () => {
    if (location.pathname.startsWith('/reports/') && location.pathname !== '/reports') {
      if (location.pathname.endsWith('/edit')) return 'Edit report'
      return 'Report detail'
    }
    return pageNames[location.pathname] || 'Safety intelligence'
  }

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
      <div className="flex items-center justify-between px-4 py-4 sm:px-6 xl:px-8">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMenuOpen}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
            aria-label="Open navigation"
          >
            <Menu size={21} />
          </button>

          <div>
            <div className="mb-1 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
              <ShieldCheck size={14} className="text-primary-600" />
              operational safety intelligence
            </div>
            <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">{getPageTitle()}</h1>
          </div>
        </div>

        <div className="flex items-center gap-3 sm:gap-5">
          <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.12em] text-emerald-700 sm:flex">
            <Radio size={12} className="text-emerald-600" />
            System online
          </div>

          <button type="button" onClick={() => setIsOpen((current) => !current)} className="relative rounded-lg border border-slate-200 p-2.5 text-slate-600 transition hover:bg-slate-100" aria-label="Notifications">
            <Bell size={18} />
            {canSeeAlerts && alerts.length > 0 && <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white ring-2 ring-white">{alerts.length}</span>}
          </button>

          {canSeeAlerts && isOpen && <div className="absolute right-4 top-16 z-30 w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-slate-200 bg-white p-3 shadow-xl">
            <div className="mb-2 flex items-center justify-between px-2"><p className="text-sm font-bold text-slate-900">Safety alerts</p><span className="text-xs text-slate-500">{alerts.length} unread</span></div>
            {alerts.length === 0 ? <p className="p-3 text-sm text-slate-500">No unread alerts.</p> : <div className="max-h-80 space-y-2 overflow-y-auto">{alerts.map((alert) => <div key={alert.alert_id} className="rounded-xl border border-red-100 bg-red-50 p-3"><div className="flex items-start justify-between gap-2"><p className="text-xs font-bold uppercase tracking-wider text-red-700">{alert.severity} alert</p><button type="button" onClick={() => markRead(alert.alert_id)} className="text-xs font-semibold text-slate-500 hover:text-slate-900">Mark read</button></div><p className="mt-1 text-sm font-semibold text-slate-900">{alert.title}</p><p className="mt-1 text-xs text-slate-600">Report #{alert.report_id?.slice(0, 8)} · {Math.round((alert.sif_probability || 0) * 100)}% SIF probability</p><Link to={`/reports/${alert.report_id}`} onClick={() => setIsOpen(false)} className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-primary-700">View report <ExternalLink size={12} /></Link></div>)}</div>}
          </div>}

          {user && (
            <div className="flex items-center gap-3 border-l border-slate-200 pl-3 sm:pl-5">
              <div className="hidden text-right sm:block">
                <div className="text-sm font-semibold text-slate-900">{user.name}</div>
                <div className="text-[11px] uppercase tracking-[0.14em] text-slate-500">{user.role.replace('_', ' ')}</div>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-50 font-semibold text-primary-700 ring-1 ring-primary-200">
                {user.name.charAt(0).toUpperCase()}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
