def calculate_student_risk(student: dict) -> dict:
    score = 0
    reasons: list[str] = []

    if student.get("duplicate_apaar"):
        score += 40
        reasons.append("APAAR ID appears across multiple institutions")
    if student.get("intake_violation"):
        score += 25
        reasons.append("Institution-course intake limit exceeded")
    if student.get("missing_required_fields"):
        score += 20
        reasons.append("Missing required student fields")
    if student.get("name_mismatch"):
        score += 15
        reasons.append("Possible name mismatch for the same APAAR ID")

    if score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    return {
        "score": min(score, 100),
        "level": level,
        "reasons": reasons,
        "human_review_required": score > 0,
        "advisory": "This is a risk indicator only and does not imply fraud.",
    }
