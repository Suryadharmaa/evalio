from datetime import date

import pytest

from api.admission_engine.engine.enums import TestPolicy as Policy
from api.admission_engine.engine.v2.academics import (
    AcademicEvaluationV2,
    AcademicRequestV2,
    AcademicTermV2,
    evaluate_academic_v2,
    native_performance,
    rank_evidence,
    theil_sen_trend,
)
from api.admission_engine.engine.v2.coursework import (
    CourseworkRequestV2,
    evaluate_coursework_v2,
)
from api.admission_engine.engine.v2.models import StatusEvaluationV2
from api.admission_engine.engine.v2.testing import (
    TestAlignmentEvaluationV2 as AlignmentEvaluationV2,
)
from api.admission_engine.engine.v2.testing import TestAlignmentRequestV2 as AlignmentRequestV2
from api.admission_engine.engine.v2.testing import evaluate_test_alignment_v2

TODAY = date(2026, 9, 20)


def _academic(grades: list[float], **changes: object) -> AcademicRequestV2:
    payload: dict[str, object] = {
        "terms": tuple(AcademicTermV2(term_order=index, average_grade=grade) for index, grade in enumerate(grades)),
        "scale_min": 0,
        "scale_max": 100,
        "grading_system": "PERCENTAGE",
        "course_rigor_score": 95,
        "evaluation_date": TODAY,
    }
    payload.update(changes)
    return AcademicRequestV2.model_validate(payload)


def _coursework(**changes: object) -> CourseworkRequestV2:
    payload: dict[str, object] = {
        "relevant_areas": 5,
        "highest_level_areas": 4,
        "core_coverage": "ALL",
        "advanced_opportunities": 10,
        "advanced_taken": 8,
        "progression": "INCREASING",
        "evaluation_date": TODAY,
    }
    payload.update(changes)
    return CourseworkRequestV2.model_validate(payload)


def _testing(**changes: object) -> AlignmentRequestV2:
    payload: dict[str, object] = {
        "policy": Policy.OPTIONAL,
        "test_type": "SAT",
        "applicant_score": 1400,
        "percentile_25": 1300,
        "percentile_50": 1400,
        "percentile_75": 1500,
        "evaluation_date": TODAY,
    }
    payload.update(changes)
    return AlignmentRequestV2.model_validate(payload)


def test_a1_high_grades_and_high_rigor() -> None:
    result = evaluate_academic_v2(_academic([95, 96, 97, 98], class_rank=5, class_size=500))
    assert isinstance(result, AcademicEvaluationV2)
    assert result.overall_score >= 95
    assert result.rubric_version == "academic-2.0.0"


def test_a2_no_advanced_courses_has_no_penalty() -> None:
    no_advanced = evaluate_coursework_v2(_coursework(advanced_opportunities=0, advanced_taken=0))
    full_use = evaluate_coursework_v2(_coursework())
    assert no_advanced.components["advanced_utilization"].score is None
    assert no_advanced.overall_score == full_use.overall_score == 95
    assert "RIGOR2-001" in {rule.rule_id for rule in no_advanced.triggered_rules}


def test_a3_theil_sen_resists_one_downward_outlier() -> None:
    score, slope = theil_sen_trend(_academic([90, 91, 92, 93, 60]))
    assert slope == 1
    assert score == 88


def test_a4_one_term_makes_trend_na_and_redistributes_weight() -> None:
    result = evaluate_academic_v2(_academic([92]))
    assert isinstance(result, AcademicEvaluationV2)
    assert result.components["trend"].score is None
    assert result.components["trend"].status == "NOT_APPLICABLE"
    assert sum(result.effective_weights.values()) == pytest.approx(1)


def test_a5_native_percentage_is_not_forced_to_four_point_scale() -> None:
    result = evaluate_academic_v2(_academic([88, 89]))
    assert isinstance(result, AcademicEvaluationV2)
    assert result.native_performance_score is not None
    assert "ACAD2-001" in {rule.rule_id for rule in result.triggered_rules}


def test_a6_rank_unavailable_has_no_achievement_penalty() -> None:
    no_rank = evaluate_academic_v2(_academic([90, 90], rank_not_published=True))
    plain = evaluate_academic_v2(_academic([90, 90]))
    assert isinstance(no_rank, AcademicEvaluationV2) and isinstance(plain, AcademicEvaluationV2)
    assert no_rank.achievement_score == plain.achievement_score
    assert "ACAD2-004" in {rule.rule_id for rule in no_rank.triggered_rules}


@pytest.mark.parametrize(("position", "expected"), [(0.5999, pytest.approx(58, abs=0.02)), (0.60, 58), (0.6001, pytest.approx(58.01, abs=0.02)), (0.95, 100)])
def test_native_scale_anchor_boundaries(position: float, expected: object) -> None:
    request = AcademicRequestV2(terms=(AcademicTermV2(term_order=1, average_grade=position),), scale_min=0, scale_max=1, evaluation_date=TODAY)
    assert native_performance(request) == expected


def test_rank_boundaries_around_top_five_percent() -> None:
    assert rank_evidence(49, 1000) > rank_evidence(50, 1000) > rank_evidence(51, 1000)  # type: ignore[operator]
    assert rank_evidence(50, 1000) == 96


@pytest.mark.parametrize(("delta", "expected"), [(0.7499, 80), (0.75, 88), (0.7501, 88), (-0.7499, 65), (-0.75, 52), (-1.5, 35)])
def test_theil_sen_threshold_boundaries(delta: float, expected: float) -> None:
    score, _ = theil_sen_trend(_academic([50, 50 + delta]))
    assert score == expected


@pytest.mark.parametrize(("highest", "expected"), [(3, 42), (4, 58), (8, 72), (12, 85), (16, 95)])
def test_challenge_vs_opportunity_thresholds(highest: int, expected: float) -> None:
    result = evaluate_coursework_v2(_coursework(relevant_areas=20, highest_level_areas=highest))
    assert result.components["challenge"].score == expected


def test_major_preparation_is_separate_from_general_rigor() -> None:
    gap = evaluate_coursework_v2(_coursework(prerequisite_map_configured=True, prerequisites_met=0, prerequisites_total=4))
    unmapped = evaluate_coursework_v2(_coursework())
    assert gap.major_preparation == "GAP"
    assert unmapped.major_preparation == "N/A"
    assert gap.overall_score == unmapped.overall_score


@pytest.mark.parametrize(("score", "expected"), [(1300, 60), (1400, 78), (1500, 92), (1600, 100), (1200, 45)])
def test_reported_percentile_alignment_anchors(score: float, expected: float) -> None:
    result = evaluate_test_alignment_v2(_testing(applicant_score=score))
    assert isinstance(result, AlignmentEvaluationV2)
    assert result.overall_score == expected


def test_t1_optional_missing_is_na_without_penalty() -> None:
    result = evaluate_test_alignment_v2(_testing(applicant_score=None))
    assert isinstance(result, StatusEvaluationV2) and result.status == "N/A"
    assert result.triggered_rules[0].rule_id == "TEST2-002"


def test_t2_required_missing_is_incomplete() -> None:
    result = evaluate_test_alignment_v2(_testing(policy=Policy.REQUIRED, applicant_score=None))
    assert isinstance(result, StatusEvaluationV2) and result.status == "REQUIREMENT_INCOMPLETE"


def test_t3_blind_excludes_even_submitted_score() -> None:
    result = evaluate_test_alignment_v2(_testing(policy=Policy.BLIND))
    assert isinstance(result, StatusEvaluationV2) and result.status == "EXCLUDED"


def test_t4_missing_median_is_never_inferred() -> None:
    result = evaluate_test_alignment_v2(_testing(applicant_score=1400, percentile_50=None))
    assert isinstance(result, AlignmentEvaluationV2)
    assert result.overall_score == 76
    assert result.median_reported is False
    assert "TEST2-005" in {rule.rule_id for rule in result.triggered_rules}


def test_t5_unresolved_program_policy_is_unknown() -> None:
    result = evaluate_test_alignment_v2(_testing(policy=Policy.PROGRAM_DEPENDENT))
    assert isinstance(result, StatusEvaluationV2) and result.status == "TEST_POLICY_UNKNOWN"


def test_phase2_results_are_repeatable() -> None:
    request = _academic([86, 88, 89], class_rank=20, class_size=400)
    assert evaluate_academic_v2(request) == evaluate_academic_v2(request)
