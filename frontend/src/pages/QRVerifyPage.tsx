import { useState } from 'react'
import type { FormEvent } from 'react'

import Layout from '../components/Layout'
import { api } from '../services/api'

export default function QRVerifyPage() {
  const [token, setToken] = useState('')
  const [response, setResponse] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    setResponse(null)
    try {
      const result = await api.get(`/qr/prototype/verify/${encodeURIComponent(token)}`)
      setResponse(result.data as Record<string, unknown>)
    } catch {
      setError('Invalid or expired prototype token.')
    }
  }

  return (
    <Layout>
      <h2 className="text-2xl font-bold text-[#0B2A5B]">Privacy-Preserving QR Verification (Prototype)</h2>
      <p className="mt-1 text-sm text-slate-600">
        Prototype only. Token includes minimal approved fields and is not a production credential signature.
      </p>

      <form className="mt-6 max-w-2xl rounded-lg border border-slate-200 bg-white p-4" onSubmit={onSubmit}>
        <label className="text-sm font-medium text-slate-700" htmlFor="token">
          Signed QR token
        </label>
        <textarea
          id="token"
          className="mt-2 h-28 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          value={token}
          onChange={(event) => setToken(event.target.value)}
        />
        <button type="submit" className="mt-3 rounded bg-[#0B2A5B] px-3 py-2 text-sm font-semibold text-white">
          Verify token
        </button>
      </form>

      {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}
      {response ? (
        <pre className="mt-4 overflow-x-auto rounded bg-slate-900 p-4 text-xs text-slate-100">
          {JSON.stringify(response, null, 2)}
        </pre>
      ) : null}
    </Layout>
  )
}
