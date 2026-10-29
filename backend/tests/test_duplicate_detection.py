from app.services.duplicate_detection import detect_possible_name_mismatches, find_duplicate_identifiers


def test_find_duplicate_identifiers_returns_only_duplicates():
    students = [
        {"student_reference_id": "S1", "apaar_id": "APAAR-1", "name": "A"},
        {"student_reference_id": "S2", "apaar_id": "APAAR-1", "name": "B"},
        {"student_reference_id": "S3", "apaar_id": "APAAR-2", "name": "C"},
    ]

    result = find_duplicate_identifiers(students)

    assert result == {"APAAR-1": ["S1", "S2"]}


def test_detect_possible_name_mismatches_for_same_apaar():
    students = [
        {"apaar_id": "APAAR-1", "name": "Aarav Mehta"},
        {"apaar_id": "APAAR-1", "name": "Arav Mehta"},
        {"apaar_id": "APAAR-2", "name": "Diya Nair"},
    ]

    result = detect_possible_name_mismatches(students)

    assert result == [{"apaar_id": "APAAR-1", "names": ["aarav mehta", "arav mehta"]}]
