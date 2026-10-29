# Pramaan — AI-Powered Student Admission Verification and College Compliance Monitoring

Pramaan is an MVP full-stack platform for authorized education stakeholders to identify possible duplicate admissions, monitor approved college intake limits, validate student records, and triage suspicious admission patterns with explainable risk scoring.

> **Important**
> - APAAR verification in this MVP is **simulated** unless an authorized official integration is configured.
> - Risk flags are indicators only and **do not imply fraud**.
> - Human review is required before final decisions.

## Tech Stack

- **Frontend:** React + Vite + TypeScript
- **UI:** Tailwind CSS (navy/white/light-blue dashboard)
- **Backend:** FastAPI + SQLAlchemy + Pydantic
- **Database:** PostgreSQL (Docker Compose) with SQL migration file
- **Charts:** Recharts
- **Authentication:** JWT + role-based access control
- **Analytics:** Rule-based transparent risk scoring (designed for future ML adapters)

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed_data.py
│   │   └── services/
│   │       ├── apaar_adapter.py
│   │       ├── duplicate_detection.py
│   │       ├── intake_monitoring.py
│   │       ├── risk_scoring.py
│   │       └── verification.py
│   ├── migrations/001_initial.sql
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Main Features

### 1) Authentication & Roles
- Login endpoint with JWT token issuance.
- Roles: `student`, `college_admin`, `regulatory_admin`.
- Role-protected API routes and frontend route-guarding.

### 2) Student Management
- Student create/list APIs.
- Stores: student reference ID, APAAR placeholder, name, DOB, institution, course, academic year, admission status.
- CSV upload endpoint with:
  - header validation
  - per-row validation
  - duplicate student reference checks
  - generated downloadable error report CSV payload

### 3) Student Verification Engine
- Required-field validation.
- Duplicate identifier detection across institutions.
- Possible name mismatch detection for same APAAR ID.
- Explicit simulated verification output.
- APAAR adapter interface for future authorized integration.

### 4) College Compliance Monitoring
- Intake approval management by institution/course/year.
- Violation detection endpoint.
- Prevents duplicate counting via unique student reference IDs.

### 5) AI Risk Analysis (Rule-Based MVP)
- Transparent score using:
  - duplicate identifier signal
  - intake violation signal
  - missing field signal
  - name mismatch signal
- Returns exact reasons, level, score, and human-review requirement.

### 6) Regulatory Dashboard
- Summary metrics endpoint for:
  - total institutions
  - processed records
  - pending cases
  - duplicate matches
  - intake violations
  - high-risk cases
- Institution risk ranking.
- Case workflow statuses: pending, under_review, resolved, dismissed.
- Audit log endpoint for administrative actions.

### 7) Privacy-Preserving QR Verification (Prototype)
- Signed QR token generation endpoint with minimal approved fields only.
- Verification endpoint clearly marked as prototype.
- No sensitive personal data embedded.

## Sample Synthetic Data

Backend startup seeds synthetic records including:
- duplicate APAAR IDs across institutions
- possible name mismatch for same APAAR ID
- missing student name case
- institution intake overrun scenario

No real student data is included.

## Setup

### Option A: Docker Compose (recommended)

1. Copy env template:
   ```bash
   cp .env.example .env
   ```
2. Start stack:
   ```bash
   docker compose up --build
   ```
3. Access:
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`

### Option B: Local manual run

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Demo Credentials (seeded)

- Regulatory admin: `reg_admin / reg123`
- College admin: `college_admin / college123`
- Student: `student_demo / student123`

## API Highlights

- `POST /auth/login`
- `GET /auth/me`
- `GET/POST /institutions`
- `POST /intake-approvals`
- `GET/POST /students`
- `POST /students/upload-csv`
- `GET /verification/student/{student_id}`
- `GET /compliance/violations`
- `GET /risk/students`
- `GET /dashboard/summary`
- `GET/POST/PATCH /cases`
- `GET /audit-logs`
- `GET /qr/prototype/token/{student_id}`
- `GET /qr/prototype/verify/{token}`

## Tests

Backend unit tests cover:
- duplicate detection
- intake monitoring (including duplicate-count prevention)
- risk scoring transparency

Run:
```bash
cd backend
pytest
```

## Limitations

- APAAR verification is simulated in MVP mode.
- Rule-based scoring is deterministic and not yet model-driven.
- Frontend currently demonstrates regulatory-admin dashboard flow only.
- Migration is provided as SQL baseline (`backend/migrations/001_initial.sql`), without Alembic workflow.

## Future Enhancements

- Official authorized APAAR API integration via adapter.
- Advanced ML anomaly detection plug-in (while keeping explainability).
- Expanded role-specific frontend experiences.
- Stronger production security hardening and deployment profile.
- Full migration lifecycle tooling (Alembic) and CI pipelines.
