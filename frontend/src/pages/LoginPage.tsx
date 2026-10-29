import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { api, setAuthToken } from '../services/api'

export default function LoginPage() {
  const [username, setUsername] = useState('reg_admin')
  const [password, setPassword] = useState('reg123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const formData = new URLSearchParams()
      formData.set('username', username)
      formData.set('password', password)
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      const token = response.data.access_token as string
      localStorage.setItem('pramaan_token', token)
      setAuthToken(token)

      const me = await api.get('/auth/me')
      localStorage.setItem('pramaan_role', me.data.role)
      navigate('/dashboard')
    } catch {
      setError('Login failed. Check credentials and backend status.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <form className="w-full max-w-md rounded-xl bg-white p-6 shadow-lg" onSubmit={onSubmit}>
        <h1 className="text-2xl font-bold text-[#0B2A5B]">Pramaan Login</h1>
        <p className="mt-2 text-sm text-slate-600">Authorized roles: Student, College Admin, Regulatory Admin</p>

        <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="username">
          Username
        </label>
        <input
          id="username"
          className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />

        <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded bg-[#0B2A5B] px-3 py-2 font-semibold text-white disabled:opacity-50"
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}
