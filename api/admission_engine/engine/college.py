from typing import Literal

from api.admission_engine.engine.enums import DataFreshness, NeedPolicy, TestPolicy
from api.admission_engine.schemas.college_evaluation import (
    ApplicationAuditRequest,
    ApplicationAuditResponse,
    CollegeEvaluationRequest,
    CollegeEvaluationResponse,
    FinancialEvaluationRequest,
    FinancialEvaluationResponse,
    PublishedRange,
)

CDS_IMPORTANCE_WEIGHTS = {
    "VERY_IMPORTANT": 1.0,
    "IMPORTANT": 0.7,
    "CONSIDERED": 0.35,
    "NOT_CONSIDERED": 0.0,
}


def _test_alignment(score: float, ranges: PublishedRange) -> float:
    a, m, b = ranges.lower, ranges.median, ranges.upper
    if score <= a:
        return max(20, 60 - (a - score) / max(1, a - (a - 100)) * 20)
    if score <= m:
        return 60 + (score - a) / max(1, m - a) * 15
    if score <= b:
        return 75 + (score - m) / max(1, b - m) * 15
    return min(100, 90 + (score - b) / max(1, b - m) * 10)


def _selectivity(
    rate: float | None,
) -> Literal["EXTREME", "VERY_HIGH", "HIGH", "MODERATE_HIGH", "MODERATE", "LOWER", "UNKNOWN"]:
    if rate is None:
        return "UNKNOWN"
    return (
        "EXTREME"
        if rate < 0.05
        else "VERY_HIGH"
        if rate < 0.10
        else "HIGH"
        if rate < 0.20
        else "MODERATE_HIGH"
        if rate < 0.40
        else "MODERATE"
        if rate < 0.60
        else "LOWER"
    )


def evaluate_college(request: CollegeEvaluationRequest) -> CollegeEvaluationResponse:
    test = None
    requirements: Literal["COMPATIBLE", "INCOMPLETE", "UNKNOWN"] = (
        "UNKNOWN"
        if not request.requirements_known
        else "COMPATIBLE"
        if request.required_materials_complete
        else "INCOMPLETE"
    )
    reasons: list[str] = []
    rules: list[str] = []
    if request.test_policy == TestPolicy.REQUIRED and request.applicant_test_score is None:
        requirements = "INCOMPLETE"
        rules.append("TEST-001")
        reasons.append("A required standardized test score is missing.")
    elif request.test_policy == TestPolicy.OPTIONAL and request.applicant_test_score is None:
        rules.append("TEST-002")
    elif request.test_policy in {TestPolicy.BLIND, TestPolicy.NOT_ACCEPTED}:
        rules.append("TEST-003")
    elif (
        request.test_policy not in {TestPolicy.BLIND, TestPolicy.NOT_ACCEPTED}
        and request.applicant_test_score is not None
        and request.published_test_range is not None
    ):
        test = _test_alignment(request.applicant_test_score, request.published_test_range)
        if request.applicant_test_score > request.published_test_range.upper:
            rules.append("TEST-004")
        elif request.applicant_test_score < request.published_test_range.lower:
            rules.append("TEST-005")
    inputs = [value for value in (request.academic_strength, test) if value is not None]
    alignment = round(sum(inputs) / len(inputs), 2) if inputs else None
    component_scores = dict(request.application_components)
    if request.academic_strength is not None:
        component_scores.setdefault("academics", request.academic_strength)
    if test is not None:
        component_scores.setdefault("testing", test)
    weighted = [
        (component_scores[name], CDS_IMPORTANCE_WEIGHTS[importance])
        for name, importance in request.cds_importance.items()
        if name in component_scores
        and importance in CDS_IMPORTANCE_WEIGHTS
        and CDS_IMPORTANCE_WEIGHTS[importance] > 0
    ]
    application_strength = (
        round(
            sum(score * weight for score, weight in weighted)
            / sum(weight for _, weight in weighted),
            2,
        )
        if weighted
        else None
    )
    cds_incomplete = request.unmapped_cds_factors > 0 or not request.cds_importance or any(
        importance not in CDS_IMPORTANCE_WEIGHTS
        or (CDS_IMPORTANCE_WEIGHTS[importance] > 0 and name not in component_scores)
        for name, importance in request.cds_importance.items()
    )
    if weighted:
        rules.append("COL-007")
        reasons.append("Application strength uses published CDS importance mapped to internal weights.")
    if cds_incomplete:
        rules.append("COL-008")
        reasons.append("Missing or unknown CDS factors reduce application-strength confidence.")
    selectivity = _selectivity(request.acceptance_rate)
    confidence_score = (
        request.profile_completeness
        + request.source_freshness_points
        + request.college_data_completeness
        + request.metric_reliability
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = (
        "HIGH" if confidence_score >= 85 else "MEDIUM" if confidence_score >= 65 else "LOW"
    )
    if request.critical_source_stale and confidence == "HIGH":
        confidence = "MEDIUM"
        rules.append("COL-001")
    if cds_incomplete and confidence == "HIGH":
        confidence = "MEDIUM"
    if request.multiple_critical_unknown:
        confidence = "LOW"
    if selectivity in {"EXTREME", "VERY_HIGH"}:
        rules.append("COL-003")
    if selectivity == "EXTREME":
        rules.append("COL-004")
    if requirements == "INCOMPLETE":
        rules.append("COL-006")
    if confidence == "LOW" or alignment is None or selectivity == "UNKNOWN":
        category: Literal[
            "HIGH_REACH", "REACH", "COMPETITIVE", "LIKELY_ISH", "INSUFFICIENT_DATA"
        ] = "INSUFFICIENT_DATA"
    elif selectivity == "EXTREME" or (selectivity == "VERY_HIGH" and alignment < 90):
        category = "HIGH_REACH"
    elif selectivity == "VERY_HIGH" or (selectivity == "HIGH" and alignment < 85) or alignment < 65:
        category = "REACH"
    elif selectivity in {"MODERATE", "LOWER"} and alignment >= 85 and requirements == "COMPATIBLE":
        category = "LIKELY_ISH"
    else:
        category = "COMPETITIVE"
    reasons.extend(
        [
            f"Institution-level selectivity is {selectivity.lower().replace('_', ' ')}.",
            f"Academic alignment is {round(alignment)}/100."
            if alignment is not None
            else "Academic alignment has insufficient data.",
        ]
    )
    return CollegeEvaluationResponse(
        academic_alignment=alignment,
        application_strength=application_strength,
        components=component_scores,
        requirements_fit=requirements,
        selectivity_risk=selectivity,
        planning_category=category,
        confidence=confidence,
        confidence_score=confidence_score,
        reasons=reasons,
        triggered_rules=rules,
    )


def evaluate_financial(request: FinancialEvaluationRequest) -> FinancialEvaluationResponse:
    reasons: list[str] = []
    rules: list[str] = []
    fit: Literal["STRONG", "POSSIBLE", "POOR", "INCOMPATIBLE", "UNKNOWN"] = "UNKNOWN"
    risk: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    if (
        request.applicant_type == "INTERNATIONAL"
        and request.requires_substantial_aid
        and request.international_need_based_aid is False
    ):
        fit, risk = "INCOMPATIBLE", "HIGH"
        rules.append("FIN-001")
        reasons.append("The college does not offer international need-based aid.")
    elif (
        request.max_family_contribution is not None
        and request.estimated_required_contribution is not None
    ):
        if request.estimated_required_contribution <= request.max_family_contribution:
            fit, risk = "STRONG", "LOW"
            rules.append("FIN-003")
        else:
            fit, risk = "POOR", "HIGH"
        reasons.append(
            "Fit compares the entered budget with the current estimated family contribution."
        )
    else:
        fit, risk = "POSSIBLE", "MEDIUM"
        reasons.append("More cost or budget data is needed.")
    if (
        request.applicant_type == "INTERNATIONAL"
        and request.requires_substantial_aid
        and request.need_policy == NeedPolicy.NEED_AWARE
    ):
        risk = "HIGH"
        rules.append("FIN-002")
        reasons.append(
            "The institution is need-aware for this applicant context; no probability penalty was calculated."
        )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = (
        "LOW"
        if request.cost_freshness == DataFreshness.UNKNOWN
        else "MEDIUM"
        if request.cost_freshness == DataFreshness.STALE
        else "HIGH"
    )
    if request.cost_freshness == DataFreshness.STALE:
        rules.append("FIN-004")
    return FinancialEvaluationResponse(
        fit=fit, risk=risk, confidence=confidence, reasons=reasons, triggered_rules=rules
    )


def audit_application(request: ApplicationAuditRequest) -> ApplicationAuditResponse:
    if not request.materials:
        issue = "College requirement data is unavailable; verify the official application checklist."
        return ApplicationAuditResponse(
            completeness_score=0,
            readiness="INCOMPLETE",
            missing_required=[],
            critical_issues=[issue],
            priorities=[issue],
            checklist=[],
        )
    required = [item for item in request.materials if item.requirement_status == "REQUIRED"]
    missing = [
        item
        for item in required
        if item.completion_status not in {"PRESENT", "SUBMITTED", "NOT_APPLICABLE"}
    ]
    passed = [
        item
        for item in required
        if item.deadline
        and item.deadline.date() < request.evaluation_date
        and item.completion_status != "SUBMITTED"
    ]
    complete_count = sum(
        item.completion_status in {"PRESENT", "SUBMITTED", "NOT_APPLICABLE"} for item in required
    )
    score = round(complete_count / len(required) * 100, 2) if required else 100.0
    readiness: Literal["COMPLETE", "INCOMPLETE", "DEADLINE_PASSED"] = (
        "DEADLINE_PASSED" if passed else "INCOMPLETE" if missing else "COMPLETE"
    )
    issues = [f"Missing required material: {item.requirement_type}" for item in missing] + [
        f"Deadline passed: {item.requirement_type}" for item in passed
    ]
    quality_actions = [
        f"Evaluate material quality: {item.requirement_type}"
        for item in request.materials
        if item.completion_status in {"PRESENT", "SUBMITTED"} and not item.quality_evaluated
    ]
    optional_actions = [
        f"Review optional material: {item.requirement_type}"
        for item in request.materials
        if item.requirement_status in {"OPTIONAL", "RECOMMENDED"}
        and item.completion_status == "MISSING"
    ]
    checklist: list[dict[str, object]] = [
        {
            "requirement_type": item.requirement_type,
            "required": item.requirement_status == "REQUIRED",
            "completion_status": item.completion_status,
            "deadline": item.deadline.isoformat() if item.deadline else None,
            "quality_status": "EVALUATED" if item.quality_evaluated else "NOT_EVALUATED",
        }
        for item in request.materials
    ]
    return ApplicationAuditResponse(
        completeness_score=score,
        readiness=readiness,
        missing_required=[item.requirement_type for item in missing],
        critical_issues=issues,
        priorities=issues + quality_actions + optional_actions,
        checklist=checklist,
    )
