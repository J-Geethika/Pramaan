import { useEffect, useMemo, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import Layout from '../components/Layout'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import { api } from '../services/api'
import type { DashboardSummary, RiskStudent } from '../services/api'

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [riskRows, setRiskRows] = useState<RiskStudent[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      setError('')
      try {
        const [summaryResponse, riskResponse] = await Promise.all([
          api.get<DashboardSummary>('/dashboard/summary'),
          api.get<RiskStudent[]>('/risk/students'),
        ])
        setSummary(summaryResponse.data)
        setRiskRows(riskResponse.data)
      } catch {
        setError('Unable to load dashboard data.')
      } finally {
        setLoading(false)
      }
    }
    void run()
  }, [])

  const filteredRows = useMemo(
    () =>
      riskRows.filter((row) => row.student_reference_id.toLowerCase().includes(search.toLowerCase().trim())),
    [riskRows, search],
  )

  const riskLevelCounts = useMemo(
    () => [
      { name: 'high', value: riskRows.filter((row) => row.risk.level === 'high').length },
      { name: 'medium', value: riskRows.filter((row) => row.risk.level === 'medium').length },
      { name: 'low', value: riskRows.filter((row) => row.risk.level === 'low').length },
    ],
    [riskRows],
  )

  return (
    <Layout>
      <header>
        <h2 className="text-2xl font-bold text-[#0B2A5B]">Regulatory Dashboard</h2>
        <p className="text-sm text-slate-600">
          Simulated verification and risk analytics only. Human review is required before any action.
        </p>
      </header>

      {loading ? <p className="mt-6 text-slate-600">Loading dashboard...</p> : null}
      {error ? <p className="mt-6 text-rose-600">{error}</p> : null}
      {!loading && !error && summary ? (
        <>
          <section className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3 xl:grid-cols-6">
            <StatCard title="Institutions" value={summary.total_institutions} />
            <StatCard title="Student Records" value={summary.student_records_processed} />
            <StatCard title="Pending Cases" value={summary.pending_verification_cases} />
            <StatCard title="Duplicate Matches" value={summary.duplicate_matches} />
            <StatCard title="Intake Violations" value={summary.intake_violations} />
            <StatCard title="High Risk" value={summary.high_risk_cases} />
          </section>

          <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h3 className="font-semibold text-slate-900">Institution Risk Ranking</h3>
              <div className="mt-4 h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={summary.institution_risk_rankings}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="institution_name" hide />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="risk_score" fill="#1e3a8a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <h3 className="font-semibold text-slate-900">Risk Distribution</h3>
              <div className="mt-4 h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={riskLevelCounts} dataKey="value" nameKey="name" outerRadius={90} fill="#0ea5e9" />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>

          <section className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h3 className="font-semibold text-slate-900">Student Risk Cases</h3>
              <input
                className="rounded border border-slate-300 px-3 py-2 text-sm"
                placeholder="Search by student reference"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>

            {filteredRows.length === 0 ? <p className="mt-4 text-sm text-slate-600">No matching records.</p> : null}
            {filteredRows.length > 0 ? (
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-600">
                      <th className="pb-2">Student Ref</th>
                      <th className="pb-2">Institution</th>
                      <th className="pb-2">Risk Score</th>
                      <th className="pb-2">Risk Level</th>
                      <th className="pb-2">Reasons</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRows.map((row) => (
                      <tr key={row.student_id} className="border-b border-slate-100 align-top">
                        <td className="py-3">{row.student_reference_id}</td>
                        <td className="py-3">{row.institution_id}</td>
                        <td className="py-3">{row.risk.score}</td>
                        <td className="py-3">
                          <StatusBadge value={row.risk.level} />
                        </td>
                        <td className="py-3 text-slate-600">{row.risk.reasons.join(', ') || 'No flags'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </section>
        </>
      ) : null}
    </Layout>
  )
}
