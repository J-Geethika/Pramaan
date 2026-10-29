from datetime import date

from sqlalchemy.orm import Session

from .auth import hash_password
from .models import AdmissionStatus, Institution, IntakeApproval, Role, Student, User


def seed_if_empty(db: Session) -> None:
    if db.query(User).first():
        return

    users = [
        User(username="student_demo", hashed_password=hash_password("student123"), role=Role.student),
        User(username="college_admin", hashed_password=hash_password("college123"), role=Role.college_admin),
        User(username="reg_admin", hashed_password=hash_password("reg123"), role=Role.regulatory_admin),
    ]
    db.add_all(users)

    institutions = [
        Institution(code="INST001", name="North Valley Engineering College"),
        Institution(code="INST002", name="Riverdale Institute of Technology"),
        Institution(code="INST003", name="Sunrise Arts and Science College"),
    ]
    db.add_all(institutions)
    db.flush()

    intake_rows = [
        IntakeApproval(institution_id=institutions[0].id, course="B.Tech CSE", academic_year="2026-27", approved_intake=2),
        IntakeApproval(institution_id=institutions[1].id, course="B.Tech CSE", academic_year="2026-27", approved_intake=2),
        IntakeApproval(institution_id=institutions[2].id, course="B.Sc Data Science", academic_year="2026-27", approved_intake=1),
    ]
    db.add_all(intake_rows)

    students = [
        Student(
            student_reference_id="SREF-0001",
            apaar_id="APAAR-900001",
            name="Aarav Mehta",
            date_of_birth=date(2007, 5, 14),
            institution_id=institutions[0].id,
            course="B.Tech CSE",
            academic_year="2026-27",
            admission_status=AdmissionStatus.approved,
        ),
        Student(
            student_reference_id="SREF-0002",
            apaar_id="APAAR-900001",
            name="Arav Mehta",
            date_of_birth=date(2007, 5, 14),
            institution_id=institutions[1].id,
            course="B.Tech CSE",
            academic_year="2026-27",
            admission_status=AdmissionStatus.pending,
        ),
        Student(
            student_reference_id="SREF-0003",
            apaar_id="APAAR-900003",
            name="Diya Nair",
            date_of_birth=date(2006, 11, 2),
            institution_id=institutions[0].id,
            course="B.Tech CSE",
            academic_year="2026-27",
            admission_status=AdmissionStatus.approved,
        ),
        Student(
            student_reference_id="SREF-0004",
            apaar_id="APAAR-900004",
            name="Ishaan Rao",
            date_of_birth=date(2006, 7, 19),
            institution_id=institutions[0].id,
            course="B.Tech CSE",
            academic_year="2026-27",
            admission_status=AdmissionStatus.approved,
        ),
        Student(
            student_reference_id="SREF-0005",
            apaar_id="APAAR-900005",
            name="",
            date_of_birth=date(2007, 1, 9),
            institution_id=institutions[2].id,
            course="B.Sc Data Science",
            academic_year="2026-27",
            admission_status=AdmissionStatus.pending,
        ),
    ]
    db.add_all(students)
    db.commit()
