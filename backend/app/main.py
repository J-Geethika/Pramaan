import csv
import io
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import authenticate_user, create_access_token, get_current_user, require_roles
from .config import settings
from .database import Base, engine, get_db
from .models import AdmissionStatus, AuditLog, CaseReview, CaseStatus, Institution, IntakeApproval, Role, Student
from .schemas import (
    CaseReviewRead,
    CaseStatusUpdate,
    InstitutionCreate,
    InstitutionRead,
    IntakeApprovalCreate,
    StudentCreate,
    StudentRead,
    Token,
)
from .seed_data import seed_if_empty
from .services.apaar_adapter import OfficialAPaarVerificationAdapter, SimulatedAPaarVerificationAdapter
from .services.duplicate_detection import detect_possible_name_mismatches, find_duplicate_identifiers
from .services.intake_monitoring import compute_intake_violations
from .services.risk_scoring import calculate_student_risk
from .services.verification import verify_student_record

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        seed_if_empty(db)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "Pramaan API"}


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return Token(access_token=token)


@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}


@app.post("/institutions", response_model=InstitutionRead)
def create_institution(
    payload: InstitutionCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.regulatory_admin)),
):
    institution = Institution(**payload.model_dump())
    db.add(institution)
    db.commit()
    db.refresh(institution)
    _log_action(db, user.username, "create_institution", "institution", str(institution.id), payload.model_dump())
    return institution


@app.get("/institutions", response_model=list[InstitutionRead])
def list_institutions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    _ = user
    return db.query(Institution).order_by(Institution.name).all()


@app.post("/intake-approvals")
def create_intake_approval(
    payload: IntakeApprovalCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.regulatory_admin)),
):
    approval = IntakeApproval(**payload.model_dump())
    db.add(approval)
    db.commit()
    db.refresh(approval)
    _log_action(db, user.username, "create_intake_approval", "intake_approval", str(approval.id), payload.model_dump())
    return {"id": approval.id}


@app.post("/students", response_model=StudentRead)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.college_admin, Role.regulatory_admin)),
):
    existing = db.query(Student).filter(Student.student_reference_id == payload.student_reference_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Duplicate student reference ID")

    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    _log_action(db, user.username, "create_student", "student", str(student.id), {"student_reference_id": student.student_reference_id})
    return student


@app.get("/students", response_model=list[StudentRead])
def list_students(
    institution_id: int | None = None,
    course: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _ = user
    query = db.query(Student)
    if institution_id:
        query = query.filter(Student.institution_id == institution_id)
    if course:
        query = query.filter(Student.course == course)
    return query.order_by(Student.id.desc()).all()


@app.post("/students/upload-csv")
def upload_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.college_admin, Role.regulatory_admin)),
):
    required_headers = {
        "student_reference_id",
        "apaar_id",
        "name",
        "date_of_birth",
        "institution_id",
        "course",
        "academic_year",
        "admission_status",
    }
    body = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(body))

    if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
        raise HTTPException(status_code=400, detail="CSV missing required headers")

    errors: list[dict] = []
    inserted = 0

    for idx, row in enumerate(reader, start=2):
        missing = [h for h in required_headers if not row.get(h)]
        if missing:
            errors.append({"line": idx, "error": f"Missing fields: {', '.join(sorted(missing))}"})
            continue
        if db.query(Student).filter(Student.student_reference_id == row["student_reference_id"]).first():
            errors.append({"line": idx, "error": "Duplicate student_reference_id"})
            continue

        try:
            status_value = AdmissionStatus(row["admission_status"])
            student = Student(
                student_reference_id=row["student_reference_id"],
                apaar_id=row["apaar_id"],
                name=row["name"],
                date_of_birth=datetime.strptime(row["date_of_birth"], "%Y-%m-%d").date(),
                institution_id=int(row["institution_id"]),
                course=row["course"],
                academic_year=row["academic_year"],
                admission_status=status_value,
            )
        except Exception:  # noqa: BLE001
            errors.append({"line": idx, "error": "Validation error in row format or field values"})
            continue

        db.add(student)
        inserted += 1

    db.commit()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["line", "error"])
    writer.writeheader()
    writer.writerows(errors)

    _log_action(db, user.username, "upload_students_csv", "student", "batch", {"inserted": inserted, "errors": len(errors)})
    return {
        "inserted": inserted,
        "errors": errors,
        "error_report_csv": output.getvalue(),
    }


@app.get("/verification/student/{student_id}")
def verify_student(student_id: int, db: Session = Depends(get_db), user=Depends(require_roles(Role.college_admin, Role.regulatory_admin))):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    all_students = db.query(Student).all()
    duplicate_map = find_duplicate_identifiers(
        [{"student_reference_id": s.student_reference_id, "apaar_id": s.apaar_id, "name": s.name} for s in all_students]
    )
    duplicate_ids = set(duplicate_map.keys())

    adapter = OfficialAPaarVerificationAdapter() if settings.apaar_official_integration_enabled else SimulatedAPaarVerificationAdapter()
    verification = verify_student_record(
        {
            "student_reference_id": student.student_reference_id,
            "apaar_id": student.apaar_id,
            "name": student.name,
            "date_of_birth": student.date_of_birth,
            "institution_id": student.institution_id,
            "course": student.course,
            "academic_year": student.academic_year,
        },
        adapter,
        duplicate_ids,
    )

    student.verification_mode = verification["verification_mode"]
    student.verification_status = "verified" if verification["verified"] else "requires_review"
    db.commit()

    _log_action(db, user.username, "verify_student", "student", str(student.id), verification)
    return verification


@app.get("/compliance/violations")
def get_intake_violations(db: Session = Depends(get_db), user=Depends(require_roles(Role.regulatory_admin))):
    intake_rows = [
        {
            "institution_id": row.institution_id,
            "course": row.course,
            "academic_year": row.academic_year,
            "approved_intake": row.approved_intake,
        }
        for row in db.query(IntakeApproval).all()
    ]
    student_rows = [
        {
            "student_reference_id": row.student_reference_id,
            "institution_id": row.institution_id,
            "course": row.course,
            "academic_year": row.academic_year,
        }
        for row in db.query(Student).all()
    ]
    return compute_intake_violations(intake_rows, student_rows)


@app.get("/risk/students")
def student_risk_view(db: Session = Depends(get_db), user=Depends(require_roles(Role.regulatory_admin))):
    students = db.query(Student).all()
    duplicate_map = find_duplicate_identifiers(
        [{"student_reference_id": s.student_reference_id, "apaar_id": s.apaar_id, "name": s.name} for s in students]
    )
    mismatches = {item["apaar_id"] for item in detect_possible_name_mismatches([{"apaar_id": s.apaar_id, "name": s.name} for s in students])}

    violations = compute_intake_violations(
        [
            {
                "institution_id": row.institution_id,
                "course": row.course,
                "academic_year": row.academic_year,
                "approved_intake": row.approved_intake,
            }
            for row in db.query(IntakeApproval).all()
        ],
        [
            {
                "student_reference_id": row.student_reference_id,
                "institution_id": row.institution_id,
                "course": row.course,
                "academic_year": row.academic_year,
            }
            for row in students
        ],
    )
    violation_keys = {(v["institution_id"], v["course"], v["academic_year"]) for v in violations}

    results = []
    for student in students:
        risk = calculate_student_risk(
            {
                "duplicate_apaar": student.apaar_id in duplicate_map,
                "name_mismatch": student.apaar_id in mismatches,
                "intake_violation": (student.institution_id, student.course, student.academic_year) in violation_keys,
                "missing_required_fields": not all(
                    [student.student_reference_id, student.apaar_id, student.name, student.date_of_birth, student.course]
                ),
            }
        )
        results.append(
            {
                "student_id": student.id,
                "student_reference_id": student.student_reference_id,
                "institution_id": student.institution_id,
                "risk": risk,
            }
        )
    return results


@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), user=Depends(require_roles(Role.regulatory_admin))):
    students = db.query(Student).all()
    duplicates = find_duplicate_identifiers(
        [{"student_reference_id": s.student_reference_id, "apaar_id": s.apaar_id, "name": s.name} for s in students]
    )
    violations = get_intake_violations(db, user)
    high_risk = [entry for entry in student_risk_view(db, user) if entry["risk"]["level"] == "high"]

    risk_by_institution: dict[int, int] = defaultdict(int)
    for entry in student_risk_view(db, user):
        risk_by_institution[entry["institution_id"]] += entry["risk"]["score"]

    institution_lookup = {inst.id: inst.name for inst in db.query(Institution).all()}
    ranked = [
        {"institution_id": inst_id, "institution_name": institution_lookup.get(inst_id, "Unknown"), "risk_score": score}
        for inst_id, score in sorted(risk_by_institution.items(), key=lambda item: item[1], reverse=True)
    ]

    pending_cases = db.query(CaseReview).filter(CaseReview.status == CaseStatus.pending).count()

    return {
        "total_institutions": db.query(Institution).count(),
        "student_records_processed": db.query(Student).count(),
        "pending_verification_cases": pending_cases,
        "duplicate_matches": len(duplicates),
        "intake_violations": len(violations),
        "high_risk_cases": len(high_risk),
        "institution_risk_rankings": ranked,
    }


@app.post("/cases", response_model=CaseReviewRead)
def create_case(payload: dict, db: Session = Depends(get_db), user=Depends(require_roles(Role.regulatory_admin))):
    case = CaseReview(
        student_id=payload.get("student_id"),
        institution_id=payload.get("institution_id"),
        case_type=payload.get("case_type", "manual_review"),
        status=CaseStatus.pending,
        reasons=payload.get("reasons", []),
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    _log_action(db, user.username, "create_case", "case_review", str(case.id), payload)
    return case


@app.get("/cases", response_model=list[CaseReviewRead])
def list_cases(status: CaseStatus | None = None, db: Session = Depends(get_db), user=Depends(require_roles(Role.regulatory_admin))):
    _ = user
    query = db.query(CaseReview)
    if status:
        query = query.filter(CaseReview.status == status)
    return query.order_by(CaseReview.created_at.desc()).all()


@app.patch("/cases/{case_id}", response_model=CaseReviewRead)
def update_case_status(
    case_id: int,
    payload: CaseStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.regulatory_admin)),
):
    case = db.query(CaseReview).filter(CaseReview.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = payload.status
    db.commit()
    db.refresh(case)
    _log_action(db, user.username, "update_case", "case_review", str(case.id), {"status": payload.status.value})
    return case


@app.get("/audit-logs")
def audit_logs(limit: int = 100, db: Session = Depends(get_db), user=Depends(require_roles(Role.regulatory_admin))):
    _ = user
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": row.id,
            "actor_username": row.actor_username,
            "action": row.action,
            "target_type": row.target_type,
            "target_id": row.target_id,
            "metadata": row.details,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.get("/qr/prototype/token/{student_id}")
def generate_qr_token(student_id: int, db: Session = Depends(get_db), user=Depends(require_roles(Role.college_admin, Role.regulatory_admin))):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    serializer = URLSafeSerializer(settings.qr_signing_secret, salt="pramaan-qr-prototype")
    payload = {
        "prototype": True,
        "student_reference_id": student.student_reference_id,
        "institution_id": student.institution_id,
        "admission_status": student.admission_status.value,
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }
    token = serializer.dumps(payload)
    return {
        "token": token,
        "notice": "Prototype token: contains only minimal approved fields and is not production-grade credential signing.",
    }


@app.get("/qr/prototype/verify/{token}")
def verify_qr_token(token: str):
    serializer = URLSafeSerializer(settings.qr_signing_secret, salt="pramaan-qr-prototype")
    try:
        payload = serializer.loads(token)
    except BadSignature as exc:
        raise HTTPException(status_code=400, detail="Invalid token") from exc

    return {
        "prototype": True,
        "official_verification": False,
        "message": "Prototype verification only. Use production-grade signing infrastructure for real credentials.",
        "verified_data": {
            "student_reference_id": payload.get("student_reference_id"),
            "institution_id": payload.get("institution_id"),
            "admission_status": payload.get("admission_status"),
            "issued_at": payload.get("issued_at"),
        },
    }


def _log_action(db: Session, actor_username: str, action: str, target_type: str, target_id: str, metadata: dict):
    log = AuditLog(
        actor_username=actor_username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=metadata,
    )
    db.add(log)
    db.commit()
