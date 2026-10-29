import { Link, useNavigate } from 'react-router-dom'

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto grid max-w-7xl grid-cols-1 md:grid-cols-[240px_1fr]">
        <aside className="bg-[#0B2A5B] p-6 text-white">
          <h1 className="text-2xl font-bold">Pramaan</h1>
          <p className="mt-2 text-sm text-blue-100">Admission Verification & Compliance</p>
          <nav className="mt-8 space-y-3 text-sm">
            <Link className="block rounded px-3 py-2 hover:bg-blue-800" to="/dashboard">
              Dashboard
            </Link>
            <Link className="block rounded px-3 py-2 hover:bg-blue-800" to="/qr-verify">
              QR Verify Prototype
            </Link>
          </nav>
          <button
            type="button"
            className="mt-8 rounded bg-white px-3 py-2 text-sm font-semibold text-[#0B2A5B]"
            onClick={() => {
              localStorage.removeItem('pramaan_token')
              localStorage.removeItem('pramaan_role')
              navigate('/login')
            }}
          >
            Logout
          </button>
        </aside>
        <main className="p-4 md:p-8">{children}</main>
      </div>
    </div>
  )
}
