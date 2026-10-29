from .apaar_adapter import APaarVerificationAdapter


def verify_student_record(student: dict, adapter: APaarVerificationAdapter, duplicate_apaar_ids: set[str]) -> dict:
    missing_fields = [
        key
        for key in ["student_reference_id", "apaar_id", "name", "date_of_birth", "institution_id", "course", "academic_year"]
        if not student.get(key)
    ]

    duplicate_flag = student.get("apaar_id") in duplicate_apaar_ids
    apaar_result = adapter.verify(student.get("apaar_id", ""), student.get("name", ""))

    return {
        "valid_required_fields": not missing_fields,
        "missing_fields": missing_fields,
        "duplicate_identifier_detected": duplicate_flag,
        "verification_mode": apaar_result.mode,
        "verified": apaar_result.verified,
        "message": apaar_result.message,
        "official_verification": False,
    }
