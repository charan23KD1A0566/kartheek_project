import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Eye, EyeOff, ShieldCheck, Sparkles } from 'lucide-react'
import { useAuthStore } from '../stores/appStore'
import { authAPI } from '../services/api'

const demoAccounts = [
  { email: 'admin@sifsentinel.demo', password: 'Admin@123', role: 'Admin' },
  { email: 'safety@sifsentinel.demo', password: 'Safety@123', role: 'Safety Officer' },
  { email: 'manager@sifsentinel.demo', password: 'Manager@123', role: 'Manager' },
  { email: 'employee@sifsentinel.demo', password: 'Employee@123', role: 'Employee' },
]

export default function LoginPage() {
  const navigate = useNavigate()
  const { setUser } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isPasswordVisible, setIsPasswordVisible] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (event) => {
    event.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await authAPI.login(email, password)
      const { access_token, user } = response.data
      setUser(user, access_token)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to sign in. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  const fillDemoCredentials = (demoEmail, demoPassword) => {
    setEmail(demoEmail)
    setPassword(demoPassword)
  }

  return (
    <div className="login-shell px-4 py-6 sm:px-6 lg:px-8">
      <div className="relative mx-auto grid min-h-[calc(100vh-2rem)] max-w-6xl items-center gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="relative hidden lg:block">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 ring-1 ring-primary-200 shadow-sm">
              <ShieldCheck size={23} />
            </div>
            <div>
              <div className="text-lg font-black uppercase tracking-[0.18em] text-slate-900">SIF</div>
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Sentinel</div>
            </div>
          </div>

          <p className="section-kicker">AI-powered safety intelligence</p>
          <h1 className="max-w-xl text-5xl font-black leading-[1.05] tracking-[-0.05em] text-slate-900 xl:text-6xl">
            Detect SIF precursors before they become incidents.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
            SIF Sentinel helps safety teams assess unsafe acts, unsafe conditions and near misses with explainable AI review and human oversight.
          </p>

          <div className="mt-10 grid max-w-xl grid-cols-3 gap-4">
            <div className="card p-4">
              <div className="text-2xl font-black text-slate-900">NLP</div>
              <div className="mt-1 text-xs font-medium uppercase tracking-[0.12em] text-slate-500">Evidence</div>
            </div>
            <div className="card p-4">
              <div className="text-2xl font-black text-slate-900">SIF</div>
              <div className="mt-1 text-xs font-medium uppercase tracking-[0.12em] text-slate-500">Risk</div>
            </div>
            <div className="card p-4">
              <div className="text-2xl font-black text-slate-900">HITL</div>
              <div className="mt-1 text-xs font-medium uppercase tracking-[0.12em] text-slate-500">Review</div>
            </div>
          </div>

          <div className="mt-10 flex items-center justify-center">
            <div className="relative h-60 w-60">
              <div className="absolute inset-5 rounded-full border border-primary-200" />
              <div className="absolute inset-9 rounded-full border border-primary-100" />
              <div className="absolute inset-0 flex items-center justify-center rounded-full bg-white shadow-[0_20px_50px_rgba(59,130,246,0.08)] ring-1 ring-slate-200">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary-50 text-primary-600 ring-1 ring-primary-200">
                  <ShieldCheck size={36} />
                </div>
              </div>
              <div className="absolute left-1/2 top-3 h-3 w-3 -translate-x-1/2 rounded-full bg-amber-400 shadow-[0_0_14px_rgba(245,158,11,0.6)]" />
              <div className="absolute right-8 top-16 h-3 w-3 rounded-full bg-primary-500 shadow-[0_0_14px_rgba(59,130,246,0.6)]" />
              <div className="absolute left-8 bottom-16 h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_14px_rgba(34,197,94,0.6)]" />
            </div>
          </div>
        </section>

        <div className="mx-auto w-full max-w-md">
          <div className="mb-6 text-center lg:hidden">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 ring-1 ring-primary-200 shadow-sm">
              <ShieldCheck size={28} />
            </div>
            <div className="mt-4 text-xl font-black uppercase tracking-[0.2em] text-slate-900">SIF</div>
          </div>

          <div className="card rounded-3xl p-6 sm:p-7">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div>
                <p className="section-kicker mb-2">Secure workspace</p>
                <h2 className="text-3xl font-black tracking-[-0.04em] text-slate-900">Welcome back</h2>
                <p className="mt-2 text-sm text-slate-500">Sign in to your safety command center.</p>
              </div>
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 text-amber-600 ring-1 ring-amber-200">
                <Sparkles size={18} />
              </div>
            </div>

            {error && (
              <div className="mb-4 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                <AlertCircle size={17} className="mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="email" className="mb-2 block text-sm font-semibold text-slate-700">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@company.com"
                  required
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-2 block text-sm font-semibold text-slate-700">Password</label>
                <div className="relative">
                  <input
                    id="password"
                    type={isPasswordVisible ? 'text' : 'password'}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setIsPasswordVisible((current) => !current)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-500 hover:bg-slate-100"
                    aria-label={isPasswordVisible ? 'Hide password' : 'Show password'}
                  >
                    {isPasswordVisible ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={isLoading} className="btn btn-primary w-full py-3 text-sm disabled:cursor-not-allowed disabled:opacity-70">
                {isLoading ? (
                  <>
                    <span className="loading-spinner mr-2" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    Enter command center
                    <ArrowRight size={16} className="ml-2" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-3 text-center text-sm font-semibold text-slate-700">Demo accounts</div>
              <div className="space-y-2">
                {demoAccounts.map((account) => (
                  <button
                    key={account.email}
                    type="button"
                    onClick={() => fillDemoCredentials(account.email, account.password)}
                    className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left transition hover:border-primary-200 hover:bg-primary-50"
                  >
                    <div className="text-sm font-semibold text-slate-800">{account.role}</div>
                    <div className="mt-1 text-xs font-medium text-primary-700">{account.email}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
