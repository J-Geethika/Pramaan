import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
})

export const setAuthToken = (token: string | null) => {
  if (!token) {
    delete api.defaults.headers.common.Authorization
    return
  }
  api.defaults.headers.common.Authorization = 'Bearer ' + token
}

export type DashboardSummary = {
  total_institutions: number
  student_records_processed: number
  pending_verification_cases: number
  duplicate_matches: number
  intake_violations: number
  high_risk_cases: number
  institution_risk_rankings: Array<{
    institution_id: number
    institution_name: string
    risk_score: number
  }>
}

export type RiskStudent = {
  student_id: number
  student_reference_id: string
  institution_id: number
  risk: {
    score: number
    level: 'low' | 'medium' | 'high'
    reasons: string[]
    human_review_required: boolean
    advisory: string
  }
}
