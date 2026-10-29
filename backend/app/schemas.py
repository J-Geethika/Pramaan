from datetime import date, datetime

from pydantic import BaseModel, Field

from .models import AdmissionStatus, CaseStatus, Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    username: str
    role: Role

    class Config:
        from_attributes = True


class InstitutionCreate(BaseModel):
    code: str
    name: str


class InstitutionRead(InstitutionCreate):
    id: int

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    student_reference_id: str = Field(min_length=3, max_length=120)
    apaar_id: str = Field(min_length=8, max_length=64)
    name: str
    date_of_birth: date
    institution_id: int
    course: str
    academic_year: str
    admission_status: AdmissionStatus = AdmissionStatus.pending


class StudentRead(StudentCreate):
    id: int
    verification_status: str
    verification_mode: str

    class Config:
        from_attributes = True


class IntakeApprovalCreate(BaseModel):
    institution_id: int
    course: str
    academic_year: str
    approved_intake: int


class CaseReviewRead(BaseModel):
    id: int
    student_id: int | None
    institution_id: int | None
    case_type: str
    status: CaseStatus
    reasons: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CaseStatusUpdate(BaseModel):
    status: CaseStatus
