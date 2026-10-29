from app.services.risk_scoring import calculate_student_risk


def test_risk_scoring_transparent_reasons_and_review_flag():
    result = calculate_student_risk(
        {
            "duplicate_apaar": True,
            "intake_violation": True,
            "missing_required_fields": False,
            "name_mismatch": True,
        }
    )

    assert result["score"] == 80
    assert result["level"] == "high"
    assert "APAAR ID appears across multiple institutions" in result["reasons"]
    assert result["human_review_required"] is True
    assert "does not imply fraud" in result["advisory"]
