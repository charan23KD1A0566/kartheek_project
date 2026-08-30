import { Link, useLocation } from 'react-router-dom'
import { BarChart3, FileText, TrendingUp, LogOut, X, ShieldCheck, Network, Plus, Brain } from 'lucide-react'
import { useAuthStore } from '../stores/appStore'

const menuItems = [
  { label: 'Dashboard', path: '/', icon: BarChart3 },
  { label: 'New Report', path: '/reports/new', icon: Plus },
  { label: 'Reports', path: '/reports', icon: FileText },
  { label: 'Analytics', path: '/analytics', icon: TrendingUp },
  { label: 'Taxonomy', path: '/taxonomy', icon: Network },
  { label: 'AI Analysis', path: '/analysis', icon: Brain },
]

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation()
  const { logout, user } = useAuthStore()

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white shadow-[0_20px_50px_rgba(15,23,42,0.08)] transition-transform duration-250 lg:sticky lg:top-0 lg:h-screen lg:w-72 lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="border-b border-slate-200 p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50 text-primary-600 shadow-sm ring-1 ring-primary-200">
            <ShieldCheck size={22} />
          </div>
          <div>
            <div className="text-lg font-extrabold tracking-[0.12em] text-slate-900">SIF</div>
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Sentinel</div>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-5 rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
          aria-label="Close navigation"
        >
          <X size={18} />
        </button>
      </div>

      <nav className="flex-1 space-y-1 p-4" aria-label="Primary navigation">
        {menuItems.filter((item) => user?.role === 'EMPLOYEE' || !['/reports/new', '/analysis'].includes(item.path)).map((item) => {
          const Icon = item.icon
          const isActive =
            location.pathname === item.path ||
            (item.path !== '/' && location.pathname.startsWith(item.path))

          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={`group flex items-center gap-3 rounded-xl px-3.5 py-3 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'border-l-2 border-primary-600 bg-primary-50 text-primary-700 shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Icon size={18} className={isActive ? 'text-primary-600' : 'text-slate-500'} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-slate-200 p-4">
        <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
          <div className="mb-1 flex items-center gap-2 font-semibold">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Pipeline active
          </div>
          <div>Reports are currently reviewed by the safety team.</div>
        </div>

        {user && (
          <div className="mb-4 rounded-xl bg-slate-100 p-3 text-sm">
            <div className="font-semibold text-slate-800">{user.name}</div>
            <div className="text-xs uppercase tracking-[0.14em] text-slate-500">{user.role.replace('_', ' ')}</div>
          </div>
        )}

        <button
          type="button"
          onClick={logout}
          className="btn btn-ghost flex w-full items-center justify-center gap-2"
        >
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}
