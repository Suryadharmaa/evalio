import pytest
from pydantic import ValidationError

from api.admission_engine.engine.coursework import evaluate_coursework
from api.admission_engine.schemas.coursework import CourseworkEvaluationRequest


def no_advanced_payload() -> dict[str, object]:
    areas = ["ENGLISH", "MATHEMATICS", "LAB_SCIENCE", "SOCIAL_SCIENCE", "FOREIGN_LANGUAGE"]
    return {
        "curriculum_type": "School curriculum", "grade_levels": [11],
        "courses": [{"course": f"Course {index}", "subject_area": area, "grade_level": 11, "course_level": "STANDARD", "is_major_related": index < 2} for index, area in enumerate(areas)],
        "advanced_courses_available": 0, "advanced_program_types": [],
        "highest_levels_available": {area: "STANDARD" for area in areas},
        "intended_major": "Economics", "school_context_notes": "The school offers no AP, IB, honors, or dual-enrollment courses.",
    }


def test_no_advanced_opportunity_uses_neutral_score_without_penalty() -> None:
    result = evaluate_coursework(CourseworkEvaluationRequest.model_validate(no_advanced_payload()))
    advanced = next(item for item in result.components if item.key == "advanced_utilization")
    assert result.no_advanced_penalty is True
    assert advanced.points == 16
    assert advanced.score is None
    assert result.triggered_rules[0]["rule_id"] == "ACAD-005"
    assert result.display_score == 91


def test_coursework_result_is_deterministic_and_exposes_all_evidence() -> None:
    payload = CourseworkEvaluationRequest.model_validate(no_advanced_payload())
    left, right = evaluate_coursework(payload), evaluate_coursework(payload)
    assert left == right
    assert len(left.components) == 5
    assert all(item.evidence and item.rule and item.explanation for item in left.components)


def test_advanced_courses_cannot_exceed_reported_opportunity() -> None:
    payload = no_advanced_payload()
    courses = payload["courses"]
    assert isinstance(courses, list)
    courses[0]["course_level"] = "AP"
    with pytest.raises(ValidationError, match="cannot exceed"):
        CourseworkEvaluationRequest.model_validate(payload)


def test_highest_level_context_is_required_for_represented_areas() -> None:
    payload = no_advanced_payload()
    payload["highest_levels_available"] = {"ENGLISH": "STANDARD"}
    with pytest.raises(ValidationError, match="every represented core area"):
        CourseworkEvaluationRequest.model_validate(payload)


def test_progression_uses_documented_grade_levels() -> None:
    payload = no_advanced_payload()
    payload["grade_levels"] = [9, 11]
    payload["advanced_courses_available"] = 1
    payload["advanced_program_types"] = ["AP"]
    courses = payload["courses"]
    highest = payload["highest_levels_available"]
    assert isinstance(courses, list) and isinstance(highest, dict)
    courses[0]["grade_level"] = 9
    courses[1]["course_level"] = "AP"
    highest["MATHEMATICS"] = "AP"
    result = evaluate_coursework(CourseworkEvaluationRequest.model_validate(payload))
    progression = next(item for item in result.components if item.key == "progression")
    assert progression.points == 10
    assert "increasing" in progression.evidence


def test_contradictory_zero_opportunity_context_is_rejected() -> None:
    payload = no_advanced_payload()
    highest = payload["highest_levels_available"]
    assert isinstance(highest, dict)
    highest["MATHEMATICS"] = "AP"
    with pytest.raises(ValidationError, match="cannot be advanced"):
        CourseworkEvaluationRequest.model_validate(payload)


def test_blank_required_text_and_elective_only_input_are_rejected() -> None:
    payload = no_advanced_payload()
    payload["curriculum_type"] = "   "
    with pytest.raises(ValidationError, match="cannot be blank"):
        CourseworkEvaluationRequest.model_validate(payload)
    payload = no_advanced_payload()
    payload["courses"] = [{"course": "Art", "subject_area": "OTHER", "grade_level": 11, "course_level": "STANDARD"}]
    with pytest.raises(ValidationError, match="canonical core area"):
        CourseworkEvaluationRequest.model_validate(payload)
