import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import QRVerifyPage from './pages/QRVerifyPage'
import { setAuthToken } from './services/api'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('pramaan_token')
  const role = localStorage.getItem('pramaan_role')

  if (!token || role !== 'regulatory_admin') {
    return <Navigate to="/login" replace />
  }

  return children
}

export default function App() {
  useEffect(() => {
    setAuthToken(localStorage.getItem('pramaan_token'))
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/qr-verify"
          element={
            <RequireAuth>
              <QRVerifyPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
