import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <div className="app-shell flex min-h-screen bg-slate-50 text-slate-900">
      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      {isMenuOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-slate-900/25 backdrop-blur-[2px] lg:hidden"
          onClick={() => setIsMenuOpen(false)}
          aria-label="Close navigation overlay"
        />
      )}

      <div className="app-main flex min-w-0 flex-1 flex-col">
        <Header onMenuOpen={() => setIsMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto bg-slate-50">
          <div className="mx-auto max-w-7xl p-4 sm:p-6 xl:p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
