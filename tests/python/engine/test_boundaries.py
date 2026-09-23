from decimal import Decimal

from api.admission_engine.engine.academic import evaluate_academic
from api.admission_engine.engine.activities import evaluate_activity_description
from api.admission_engine.engine.college import evaluate_college, evaluate_financial
from api.admission_engine.engine.essay import evaluate_essay
from api.admission_engine.schemas.academic import AcademicEvaluationRequest, AcademicTermInput
from api.admission_engine.schemas.activities import ActivityDescriptionRequest
from api.admission_engine.schemas.college_evaluation import (
    CollegeEvaluationRequest,
    FinancialEvaluationRequest,
)
from api.admission_engine.schemas.essay import EssayEvaluationRequest


def test_academic_scale_boundaries_are_clamped() -> None:
    low = evaluate_academic(
        AcademicEvaluationRequest(
            terms=[AcademicTermInput(term_order=1, average_grade=Decimal(0))],
            scale_min=0,
            scale_max=100,
        )
    )
    high = evaluate_academic(
        AcademicEvaluationRequest(
            terms=[AcademicTermInput(term_order=1, average_grade=Decimal(100))],
            scale_min=0,
            scale_max=100,
        )
    )
    assert low.overall_score is not None and 0 <= low.overall_score <= 100
    assert high.overall_score is not None and 0 <= high.overall_score <= 100
    assert high.overall_score > low.overall_score


def test_empty_organization_does_not_create_false_specificity() -> None:
    result = evaluate_activity_description(
        ActivityDescriptionRequest(description="Led 12", organization="")
    )
    assert result.components["specificity"] < 95


def test_same_text_always_produces_same_result_and_never_echoes_raw_text() -> None:
    request = EssayEvaluationRequest(
        text="I built a solar cart for 12 students. I learned why measured iteration matters.",
        min_words=0,
    )
    left = evaluate_essay(request)
    right = evaluate_essay(request)
    assert left == right
    assert request.text not in left.model_dump_json()


def test_college_outputs_are_categories_not_probabilities() -> None:
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            acceptance_rate=0.04,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )
    assert result.planning_category == "HIGH_REACH"
    assert "probability" not in result.model_dump()


def test_financial_unknowns_reduce_confidence() -> None:
    result = evaluate_financial(
        FinancialEvaluationRequest(applicant_type="INTERNATIONAL", requires_substantial_aid=True)
    )
    assert result.fit == "POSSIBLE"
    assert result.confidence == "LOW"
