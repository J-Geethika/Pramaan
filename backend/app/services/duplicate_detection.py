def find_duplicate_identifiers(students: list[dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for student in students:
        grouped.setdefault(student["apaar_id"], []).append(student["student_reference_id"])
    return {apaar: refs for apaar, refs in grouped.items() if len(set(refs)) > 1}


def detect_possible_name_mismatches(students: list[dict]) -> list[dict]:
    by_apaar: dict[str, set[str]] = {}
    for student in students:
        normalized = " ".join(student["name"].lower().split())
        by_apaar.setdefault(student["apaar_id"], set()).add(normalized)

    return [
        {"apaar_id": apaar_id, "names": sorted(names)}
        for apaar_id, names in by_apaar.items()
        if len(names) > 1
    ]
