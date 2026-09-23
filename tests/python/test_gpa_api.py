from fastapi.testclient import TestClient

from api.index import app


def test_gpa_endpoint_returns_versioned_result_without_caching() -> None:
    response = TestClient(app).post(
        "/api/v1/calculators/gpa",
        json={"mode": "US_COURSES", "courses": [{"course": "Biology", "grade": "A", "course_level": "AP", "credits": 1}], "weighting_method": "HONORS_0_5_ADVANCED_1_0"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["result"]["weighted_gpa"] == 5
    assert response.json()["meta"]["calculator_version"] == "gpa-calculator-1.0.0"
    assert response.headers["cache-control"] == "no-store"
