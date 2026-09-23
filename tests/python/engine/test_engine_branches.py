from datetime import UTC, date, datetime, timedelta

import pytest

from api.admission_engine.engine.college import (
    audit_application,
    evaluate_college,
    evaluate_financial,
)
from api.admission_engine.engine.enums import (
    CompletionStatus,
    DataFreshness,
    NeedPolicy,
    RequirementStatus,
)
from api.admission_engine.engine.enums import TestPolicy as CollegeTestPolicy
from api.admission_engine.engine.honors import evaluate_honor
from api.admission_engine.engine.profile_strength import evaluate_profile_strength
from api.admission_engine.engine.scoring import weighted_score
from api.admission_engine.schemas.college_evaluation import (
    ApplicationAuditRequest,
    CollegeEvaluationRequest,
    FinancialEvaluationRequest,
    MaterialStatus,
    PublishedRange,
)
from api.admission_engine.schemas.honors import HonorInput
from api.admission_engine.schemas.profile_strength import ProfileStrengthRequest


@pytest.mark.parametrize(
    ("score", "expected"),
    [(1200, 40.0), (1350, 67.5), (1450, 82.5), (1600, 100.0)],
)
def test_test_alignment_bands(score: float, expected: float) -> None:
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=80,
            applicant_test_score=score,
            published_test_range=PublishedRange(lower=1300, median=1400, upper=1500),
            acceptance_rate=0.3,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )
    assert result.academic_alignment == (80 + expected) / 2


@pytest.mark.parametrize(
    ("rate", "risk"),
    [
        (None, "UNKNOWN"),
        (0.04, "EXTREME"),
        (0.08, "VERY_HIGH"),
        (0.15, "HIGH"),
        (0.3, "MODERATE_HIGH"),
        (0.5, "MODERATE"),
        (0.7, "LOWER"),
    ],
)
def test_selectivity_boundaries(rate: float | None, risk: str) -> None:
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            acceptance_rate=rate,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )
    assert result.selectivity_risk == risk


def test_required_test_and_confidence_caps() -> None:
    missing = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            test_policy=CollegeTestPolicy.REQUIRED,
            acceptance_rate=0.3,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
            critical_source_stale=True,
        )
    )
    assert missing.requirements_fit == "INCOMPLETE"
    assert missing.confidence == "MEDIUM"


def test_college_application_strength_uses_cds_weights() -> None:
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            application_components={"activities": 70, "essay": 80},
            cds_importance={
                "academics": "VERY_IMPORTANT",
                "activities": "IMPORTANT",
                "essay": "CONSIDERED",
                "recommendations": "NOT_CONSIDERED",
            },
            acceptance_rate=0.3,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )

    assert result.application_strength == 81.46
    assert result.confidence == "HIGH"
    assert "COL-007" in result.triggered_rules
    assert "COL-008" not in result.triggered_rules


def test_unknown_cds_signal_is_excluded_and_caps_confidence() -> None:
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            cds_importance={"academics": "VERY_IMPORTANT", "essay": "UNKNOWN"},
            unmapped_cds_factors=1,
            acceptance_rate=0.3,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )

    assert result.application_strength == 90
    assert result.confidence == "MEDIUM"
    assert "COL-008" in result.triggered_rules


def test_unknown_requirements_are_not_marked_compatible() -> None:
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=85,
            requirements_known=False,
            cds_importance={"academics": "IMPORTANT"},
            acceptance_rate=0.3,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )

    assert result.requirements_fit == "UNKNOWN"
    unknown = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            acceptance_rate=0.3,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
            multiple_critical_unknown=True,
        )
    )
    assert unknown.planning_category == "INSUFFICIENT_DATA"


def test_financial_fit_branches() -> None:
    incompatible = evaluate_financial(
        FinancialEvaluationRequest(
            applicant_type="INTERNATIONAL",
            requires_substantial_aid=True,
            international_need_based_aid=False,
            need_policy=NeedPolicy.NEED_AWARE,
            cost_freshness=DataFreshness.CURRENT,
        )
    )
    assert incompatible.fit == "INCOMPATIBLE" and {"FIN-001", "FIN-002"} <= set(
        incompatible.triggered_rules
    )
    strong = evaluate_financial(
        FinancialEvaluationRequest(
            applicant_type="DOMESTIC",
            requires_substantial_aid=False,
            max_family_contribution=50_000,
            estimated_required_contribution=40_000,
            cost_freshness=DataFreshness.CURRENT,
        )
    )
    assert strong.fit == "STRONG" and strong.confidence == "HIGH"
    poor = evaluate_financial(
        FinancialEvaluationRequest(
            applicant_type="DOMESTIC",
            requires_substantial_aid=False,
            max_family_contribution=20_000,
            estimated_required_contribution=40_000,
            cost_freshness=DataFreshness.STALE,
        )
    )
    assert poor.fit == "POOR" and "FIN-004" in poor.triggered_rules


def test_application_audit_deadline_missing_and_complete() -> None:
    yesterday = datetime.now(UTC) - timedelta(days=1)
    result = audit_application(
        ApplicationAuditRequest(
            evaluation_date=date.today(),
            materials=[
                MaterialStatus(
                    requirement_type="Essay",
                    requirement_status=RequirementStatus.REQUIRED,
                    completion_status=CompletionStatus.MISSING,
                    deadline=yesterday,
                ),
                MaterialStatus(
                    requirement_type="Transcript",
                    requirement_status=RequirementStatus.REQUIRED,
                    completion_status=CompletionStatus.SUBMITTED,
                    quality_evaluated=True,
                ),
                MaterialStatus(
                    requirement_type="Optional portfolio",
                    requirement_status=RequirementStatus.OPTIONAL,
                    completion_status=CompletionStatus.NOT_EVALUATED,
                ),
            ],
        )
    )
    assert result.readiness == "DEADLINE_PASSED"
    assert result.completeness_score == 50
    assert "Review optional material: Optional portfolio" not in result.priorities
    assert (
        audit_application(
            ApplicationAuditRequest(evaluation_date=date.today(), materials=[])
        ).readiness
        == "INCOMPLETE"
    )


def test_application_audit_prioritizes_quality_after_completeness() -> None:
    result = audit_application(
        ApplicationAuditRequest(
            evaluation_date=date.today(),
            materials=[
                MaterialStatus(
                    requirement_type="Essay",
                    requirement_status=RequirementStatus.REQUIRED,
                    completion_status=CompletionStatus.PRESENT,
                ),
                MaterialStatus(
                    requirement_type="Portfolio",
                    requirement_status=RequirementStatus.RECOMMENDED,
                    completion_status=CompletionStatus.MISSING,
                ),
            ],
        )
    )
    assert result.readiness == "COMPLETE"
    assert result.priorities == [
        "Evaluate material quality: Essay",
        "Review optional material: Portfolio",
    ]


def test_profile_strength_redistributes_missing_weights() -> None:
    empty = evaluate_profile_strength(ProfileStrengthRequest())
    assert empty.score is None and empty.effective_weights == {}
    complete = evaluate_profile_strength(ProfileStrengthRequest(academics=100, activities=50))
    assert complete.display_score == 79
    assert sum(complete.effective_weights.values()) == pytest.approx(1, abs=0.00001)


@pytest.mark.parametrize("selection_rate", [0.005, 0.03, 0.08, 0.2, 0.4, 0.8])
def test_honor_selectivity_bands(selection_rate: float) -> None:
    result = evaluate_honor(
        HonorInput(
            honor_name="Award",
            scope="NATIONAL",
            placement="FIRST",
            academic_relevance=15,
            selection_rate=selection_rate,
        )
    )
    assert 0 <= result.overall_score <= 100


def test_honor_unknown_and_unsupported_international_claim() -> None:
    unknown = evaluate_honor(
        HonorInput(honor_name="Award", scope=None, placement="PARTICIPANT", academic_relevance=0)
    )
    assert unknown.confidence == "LOW" and "HON-001" in unknown.triggered_rules
    unsupported = evaluate_honor(
        HonorInput(
            honor_name="Award", scope="INTERNATIONAL", placement="FIRST", academic_relevance=15
        )
    )
    assert unsupported.scope == 27 and "HON-004" in unsupported.triggered_rules


def test_weighted_score_empty_and_invalid_denominator() -> None:
    assert weighted_score({}, {}) is None
    assert weighted_score({"a": 50}, {"a": 0}) is None
