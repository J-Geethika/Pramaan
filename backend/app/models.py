import enum
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Role(str, enum.Enum):
    student = "student"
    college_admin = "college_admin"
    regulatory_admin = "regulatory_admin"


class AdmissionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class CaseStatus(str, enum.Enum):
    pending = "pending"
    under_review = "under_review"
    resolved = "resolved"
    dismissed = "dismissed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    students: Mapped[list["Student"]] = relationship(back_populates="institution")
    intake_approvals: Mapped[list["IntakeApproval"]] = relationship(back_populates="institution")


class IntakeApproval(Base):
    __tablename__ = "intake_approvals"
    __table_args__ = (UniqueConstraint("institution_id", "course", "academic_year", name="uq_intake_course_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    course: Mapped[str] = mapped_column(String(120), index=True)
    academic_year: Mapped[str] = mapped_column(String(20), index=True)
    approved_intake: Mapped[int] = mapped_column(Integer)

    institution: Mapped[Institution] = relationship(back_populates="intake_approvals")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_reference_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    apaar_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[date] = mapped_column(Date)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), index=True)
    course: Mapped[str] = mapped_column(String(120))
    academic_year: Mapped[str] = mapped_column(String(20), index=True)
    admission_status: Mapped[AdmissionStatus] = mapped_column(Enum(AdmissionStatus), default=AdmissionStatus.pending)
    verification_status: Mapped[str] = mapped_column(String(30), default="unverified")
    verification_mode: Mapped[str] = mapped_column(String(30), default="simulated")

    institution: Mapped[Institution] = relationship(back_populates="students")


class CaseReview(Base):
    __tablename__ = "case_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True)
    case_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.pending)
    reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_username: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(120))
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[str] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
