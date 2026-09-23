from fastapi.testclient import TestClient

from api.index import app


def no_advanced_payload() -> dict[str, object]:
    areas = ["ENGLISH", "MATHEMATICS", "LAB_SCIENCE", "SOCIAL_SCIENCE", "FOREIGN_LANGUAGE"]
    return {
        "curriculum_type": "School curriculum", "grade_levels": [11],
        "courses": [{"course": f"Course {index}", "subject_area": area, "grade_level": 11, "course_level": "STANDARD", "is_major_related": index < 2} for index, area in enumerate(areas)],
        "advanced_courses_available": 0, "advanced_program_types": [],
        "highest_levels_available": {area: "STANDARD" for area in areas},
        "intended_major": "Economics", "school_context_notes": "No advanced courses are offered.",
    }


def test_coursework_endpoint_is_versioned_and_not_cached() -> None:
    response = TestClient(app).post("/api/v1/evaluations/coursework", json=no_advanced_payload())
    assert response.status_code == 200
    assert response.json()["meta"]["rubric_version"] == "coursework-1.0.0"
    assert response.json()["data"]["evaluation"]["no_advanced_penalty"] is True
    assert response.headers["cache-control"] == "no-store"
