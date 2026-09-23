import pytest
from pydantic import ValidationError

from api.admission_engine.engine.gpa import calculate_gpa
from api.admission_engine.schemas.gpa import GpaCalculationRequest


def test_us_gpa_uses_credits_and_selected_weighting_method() -> None:
    payload = GpaCalculationRequest.model_validate(
        {
            "mode": "US_COURSES",
            "weighting_method": "HONORS_0_5_ADVANCED_1_0",
            "courses": [
                {"course": "English", "grade": "A", "course_level": "REGULAR", "credits": 1},
                {"course": "Calculus", "grade": "B", "course_level": "AP", "credits": 2},
            ],
        }
    )
    result = calculate_gpa(payload)

    assert result.unweighted_gpa == pytest.approx(3.333)
    assert result.weighted_gpa == pytest.approx(4.0)
    assert result.total_credits_or_weight == 3
    assert result.breakdown[1].weighted_value == 4
    assert "selected course-level offset" in result.formula[1]


def test_no_weighting_keeps_weighted_and_unweighted_equal() -> None:
    payload = GpaCalculationRequest.model_validate(
        {"mode": "US_COURSES", "courses": [{"course": "History", "grade": "A-", "course_level": "HONORS", "credits": 1}]}
    )
    result = calculate_gpa(payload)
    assert result.unweighted_gpa == result.weighted_gpa == 3.7


def test_international_average_preserves_raw_scale() -> None:
    payload = GpaCalculationRequest.model_validate(
        {
            "mode": "INTERNATIONAL_RAW", "curriculum_name": "Indonesia national curriculum",
            "scale_min": 0, "scale_max": 100,
            "international_grades": [{"label": "Term 1", "value": 90, "weight": 1}, {"label": "Term 2", "value": 92, "weight": 3}],
        }
    )
    result = calculate_gpa(payload)
    assert result.academic_average == 91.5
    assert result.conversion == "NOT_APPLIED"
    assert result.unweighted_gpa is None


def test_international_grade_outside_scale_is_rejected() -> None:
    with pytest.raises(ValidationError, match="within the selected scale"):
        GpaCalculationRequest.model_validate(
            {"mode": "INTERNATIONAL_RAW", "curriculum_name": "Custom", "scale_min": 0, "scale_max": 100, "international_grades": [{"label": "Term", "value": 101}]}
        )


def test_custom_weighting_requires_documented_offsets() -> None:
    with pytest.raises(ValidationError, match="custom_offsets"):
        GpaCalculationRequest.model_validate(
            {"mode": "US_COURSES", "weighting_method": "CUSTOM", "courses": [{"course": "Math", "grade": "A", "credits": 1}]}
        )
