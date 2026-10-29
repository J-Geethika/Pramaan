from app.services.intake_monitoring import compute_intake_violations


def test_intake_monitoring_prevents_duplicate_counting_and_flags_excess():
    intake_rows = [
        {"institution_id": 1, "course": "B.Tech", "academic_year": "2026-27", "approved_intake": 2},
    ]
    student_rows = [
        {"student_reference_id": "S1", "institution_id": 1, "course": "B.Tech", "academic_year": "2026-27"},
        {"student_reference_id": "S2", "institution_id": 1, "course": "B.Tech", "academic_year": "2026-27"},
        {"student_reference_id": "S2", "institution_id": 1, "course": "B.Tech", "academic_year": "2026-27"},
        {"student_reference_id": "S3", "institution_id": 1, "course": "B.Tech", "academic_year": "2026-27"},
    ]

    result = compute_intake_violations(intake_rows, student_rows)

    assert len(result) == 1
    assert result[0]["admissions_count"] == 3
    assert result[0]["excess"] == 1
