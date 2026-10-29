-- Initial schema migration for Pramaan MVP
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS institutions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS intake_approvals (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER NOT NULL REFERENCES institutions(id),
    course VARCHAR(120) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    approved_intake INTEGER NOT NULL,
    CONSTRAINT uq_intake_course_year UNIQUE (institution_id, course, academic_year)
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    student_reference_id VARCHAR(120) UNIQUE NOT NULL,
    apaar_id VARCHAR(64) NOT NULL,
    name VARCHAR(200) NOT NULL,
    date_of_birth DATE NOT NULL,
    institution_id INTEGER NOT NULL REFERENCES institutions(id),
    course VARCHAR(120) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    admission_status VARCHAR(30) NOT NULL,
    verification_status VARCHAR(30) NOT NULL DEFAULT 'unverified',
    verification_mode VARCHAR(30) NOT NULL DEFAULT 'simulated'
);

CREATE TABLE IF NOT EXISTS case_reviews (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    institution_id INTEGER REFERENCES institutions(id),
    case_type VARCHAR(80) NOT NULL,
    status VARCHAR(30) NOT NULL,
    reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    actor_username VARCHAR(100) NOT NULL,
    action VARCHAR(120) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
