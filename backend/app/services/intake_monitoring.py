def compute_intake_violations(intake_rows: list[dict], student_rows: list[dict]) -> list[dict]:
    approved = {
        (row["institution_id"], row["course"], row["academic_year"]): row["approved_intake"] for row in intake_rows
    }
    unique_students_by_key: dict[tuple[int, str, str], set[str]] = {}

    for student in student_rows:
        key = (student["institution_id"], student["course"], student["academic_year"])
        unique_students_by_key.setdefault(key, set()).add(student["student_reference_id"])

    violations: list[dict] = []
    for key, unique_refs in unique_students_by_key.items():
        approved_intake = approved.get(key)
        if approved_intake is None:
            continue
        count = len(unique_refs)
        if count > approved_intake:
            violations.append(
                {
                    "institution_id": key[0],
                    "course": key[1],
                    "academic_year": key[2],
                    "approved_intake": approved_intake,
                    "admissions_count": count,
                    "excess": count - approved_intake,
                }
            )
    return violations
