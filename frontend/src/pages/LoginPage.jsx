import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Eye, EyeOff, ShieldCheck } from 'lucide-react'
import { useAuthStore } from '../stores/appStore'
import { authAPI } from '../services/api'

const demoAccounts = [
  { label: 'Admin', email: 'admin@sifsentinel.demo', password: 'Admin@123' },
  { label: 'Safety Officer', email: 'safety@sifsentinel.demo', password: 'Safety@123' },
  { label: 'Manager', email: 'manager@sifsentinel.demo', password: 'Manager@123' },
  { label: 'Employee', email: 'employee@sifsentinel.demo', password: 'Employee@123' },
]

export default function LoginPage() {
  const navigate = useNavigate()
  const setUser = useAuthStore((state) => state.setUser)
  const [isRegistering, setIsRegistering] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggleMode = () => {
    setIsRegistering((value) => !value)
    setName('')
    setEmail('')
    setPassword('')
    setConfirmPassword('')
    setError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = isRegistering
        ? await authAPI.register(name.trim(), email.trim().toLowerCase(), password, confirmPassword)
        : await authAPI.login(email.trim().toLowerCase(), password)
      const { access_token: accessToken, user } = response.data
      setUser(user, accessToken)
      navigate('/', { replace: true })
    } catch (requestError) {
      const detail = requestError.response?.data?.detail
      if (!requestError.response) {
        setError('Cannot reach the authentication server. Make sure the backend is running and try again.')
      } else if (Array.isArray(detail)) {
        setError(detail.map((item) => item.msg).filter(Boolean).join('. '))
      } else if (requestError.response.status >= 500) {
        setError(typeof detail === 'string' ? detail : 'The authentication server failed. Please try again.')
      } else {
        setError(typeof detail === 'string' ? detail : 'Please check the highlighted account details and try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (account) => {
    setIsRegistering(false)
    setEmail(account.email)
    setPassword(account.password)
    setError('')
  }

  return (
    <main className="login-shell min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden lg:block">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 ring-1 ring-primary-200"><ShieldCheck size={24} /></div>
            <div><div className="text-lg font-black tracking-[0.2em] text-slate-900">SIF</div><div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Sentinel</div></div>
          </div>
          <p className="section-kicker">AI-powered safety intelligence</p>
          <h1 className="mt-3 max-w-xl text-6xl font-black leading-[1.05] tracking-[-0.05em] text-slate-900">Detect precursors before they become incidents.</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">A focused command center for explainable SIF risk detection, safety review, and operational action.</p>
        </section>

        <section className="mx-auto w-full max-w-md">
          <div className="mb-6 text-center lg:hidden"><div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 ring-1 ring-primary-200"><ShieldCheck size={28} /></div><p className="mt-4 text-xl font-black tracking-[0.2em] text-slate-900">SIF SENTINEL</p></div>
          <div className="card rounded-3xl p-6 sm:p-8">
            <p className="section-kicker">Secure workspace</p>
            <h2 className="mt-2 text-3xl font-black tracking-[-0.04em] text-slate-900">{isRegistering ? 'Create Account' : 'Welcome back'}</h2>
            <p className="mt-2 text-sm text-slate-500">{isRegistering ? 'Create an employee account.' : 'Sign in to your safety command center.'}</p>
            {error && <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"><AlertCircle size={17} className="mt-0.5 shrink-0" /><span>{error}</span></div>}
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              {isRegistering && <div><label htmlFor="name" className="mb-2 block text-sm font-semibold text-slate-700">Name</label><input id="name" value={name} onChange={(event) => setName(event.target.value)} required /></div>}
              <div><label htmlFor="email" className="mb-2 block text-sm font-semibold text-slate-700">Email</label><input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
              <div><label htmlFor="password" className="mb-2 block text-sm font-semibold text-slate-700">Password</label><div className="relative"><input id="password" type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} required /><button type="button" onClick={() => setShowPassword((value) => !value)} className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-slate-500" aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></div>
              {isRegistering && <div><label htmlFor="confirm-password" className="mb-2 block text-sm font-semibold text-slate-700">Confirm Password</label><input id="confirm-password" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /></div>}
              <button type="submit" disabled={loading} className="btn btn-primary flex w-full items-center justify-center py-3 disabled:opacity-60">{loading ? 'Please wait...' : isRegistering ? 'Create Account' : 'Sign In'} {!loading && <ArrowRight size={16} className="ml-2" />}</button>
            </form>
            <div className="mt-5 text-center text-sm text-slate-600">{isRegistering ? 'Already have an account?' : 'Need an account?'} <button type="button" onClick={toggleMode} className="font-semibold text-primary-600">{isRegistering ? 'Sign in' : 'Create Account'}</button></div>
            {!isRegistering && <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4"><p className="mb-3 text-center text-sm font-semibold text-slate-700">Demo Accounts</p><div className="grid grid-cols-2 gap-2">{demoAccounts.map((account) => <button key={account.email} type="button" onClick={() => fillDemo(account)} className="rounded-xl border border-slate-200 bg-white px-3 py-3 text-left text-sm font-semibold text-slate-700 hover:border-primary-300 hover:bg-primary-50">{account.label}</button>)}</div></div>}
          </div>
        </section>
      </div>
    </main>
  )
}
