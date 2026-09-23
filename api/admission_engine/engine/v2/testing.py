from datetime import date
from typing import Literal

from pydantic import model_validator

from api.admission_engine.config import V2_RUBRIC_VERSIONS
from api.admission_engine.engine.enums import (
    ConfidenceLevel,
    EvaluationStatus,
    RuleSeverity,
    TestPolicy,
)
from api.admission_engine.engine.models import ComponentResult, StrictModel
from api.admission_engine.engine.scoring import clamp, round_display, round_internal
from api.admission_engine.engine.v2.models import (
    ConfidenceV2,
    NumericEvaluationV2,
    RuleResultV2,
    StatusEvaluationV2,
)

TestType = Literal["SAT", "ACT"]


class TestAlignmentRequestV2(StrictModel):
    policy: TestPolicy
    resolved_program_policy: TestPolicy | None = None
    test_type: TestType = "SAT"
    applicant_score: float | None = None
    percentile_25: float | None = None
    percentile_50: float | None = None
    percentile_75: float | None = None
    evaluation_date: date

    @model_validator(mode="after")
    def validate_scores(self) -> "TestAlignmentRequestV2":
        minimum, maximum = (400, 1600) if self.test_type == "SAT" else (1, 36)
        supplied = [value for value in (self.applicant_score, self.percentile_25, self.percentile_50, self.percentile_75) if value is not None]
        if any(value < minimum or value > maximum for value in supplied):
            raise ValueError(f"{self.test_type} values must be between {minimum} and {maximum}")
        percentiles = [value for value in (self.percentile_25, self.percentile_50, self.percentile_75) if value is not None]
        if percentiles != sorted(percentiles):
            raise ValueError("reported test percentiles must be monotonic")
        if self.policy != TestPolicy.PROGRAM_DEPENDENT and self.resolved_program_policy is not None:
            raise ValueError("resolved_program_policy applies only to PROGRAM_DEPENDENT")
        if self.resolved_program_policy == TestPolicy.PROGRAM_DEPENDENT:
            raise ValueError("resolved program policy must be concrete")
        return self


class TestAlignmentEvaluationV2(NumericEvaluationV2):
    test_type: TestType
    median_reported: bool


def _rule(rule_id: str, title: str, trigger: str, effect: str, evidence: dict[str, object], severity: RuleSeverity = RuleSeverity.INFO) -> RuleResultV2:
    return RuleResultV2(rule_id=rule_id, domain="TEST", category="College Test Alignment", severity=severity, title=title, trigger=trigger, evidence=evidence, effect=effect, message=effect, confidence=ConfidenceLevel.HIGH, methodology_ref="SCORING_SPEC_V2.md#part-c--testing")


def _status(request: TestAlignmentRequestV2, status: str, confidence: float, rules: list[RuleResultV2]) -> StatusEvaluationV2:
    return StatusEvaluationV2(rubric_version=V2_RUBRIC_VERSIONS["testing"], status=status, evidence={"policy": request.policy.value, "test_type": request.test_type}, triggered_rules=tuple(rules), confidence=ConfidenceV2.from_score(confidence), evaluation_date=request.evaluation_date)


def _linear(value: float, left_x: float, left_y: float, right_x: float, right_y: float) -> float:
    if right_x == left_x:
        return max(left_y, right_y)
    return left_y + (value - left_x) / (right_x - left_x) * (right_y - left_y)


def evaluate_test_alignment_v2(request: TestAlignmentRequestV2) -> TestAlignmentEvaluationV2 | StatusEvaluationV2:
    rules: list[RuleResultV2] = []
    policy = request.policy
    if policy == TestPolicy.PROGRAM_DEPENDENT:
        if request.resolved_program_policy is None:
            rules.append(_rule("TEST2-004", "Program Policy Unresolved", "Program-dependent policy has no target-program resolution", "Return TEST_POLICY_UNKNOWN and reduce confidence.", {}, RuleSeverity.HIGH))
            return _status(request, "TEST_POLICY_UNKNOWN", 50, rules)
        policy = request.resolved_program_policy
    if policy in {TestPolicy.BLIND, TestPolicy.NOT_ACCEPTED}:
        rules.append(_rule("TEST2-003", "Test Blind", "College does not consider the submitted test", "Testing is excluded entirely.", {"policy": policy.value}))
        return _status(request, "EXCLUDED", 100, rules)
    if request.applicant_score is None:
        if policy == TestPolicy.REQUIRED:
            rules.append(_rule("TEST2-001", "Required Test Missing", "Required policy and no valid accepted score", "Return REQUIREMENT_INCOMPLETE.", {}, RuleSeverity.CRITICAL))
            return _status(request, "REQUIREMENT_INCOMPLETE", 100, rules)
        if policy in {TestPolicy.OPTIONAL, TestPolicy.FLEXIBLE, TestPolicy.OPTIONAL_FOR_INTL_OUTSIDE_US, TestPolicy.OPTIONAL_WITH_PROGRAM_EXCEPTIONS}:
            rules.append(_rule("TEST2-002", "Optional Test Missing", "Optional/flexible policy and no valid score", "Test Alignment is N/A with no penalty.", {}))
            return _status(request, "N/A", 100, rules)
        return _status(request, "TEST_POLICY_UNKNOWN", 40, rules)
    if request.percentile_25 is None or request.percentile_75 is None:
        return _status(request, "INSUFFICIENT_DATA", 40, rules)
    p25, p50, p75 = request.percentile_25, request.percentile_50, request.percentile_75
    score = request.applicant_score
    maximum = 1600.0 if request.test_type == "SAT" else 36.0
    minimum_span = 80.0 if request.test_type == "SAT" else 3.0
    if score < p25:
        alignment = 60 - 30 * ((p25 - score) / max(p75 - p25, minimum_span))
        alignment = max(20, alignment)
    elif p50 is not None and score <= p50:
        alignment = _linear(score, p25, 60, p50, 78)
    elif p50 is not None and score <= p75:
        alignment = _linear(score, p50, 78, p75, 92)
    elif score <= p75:
        alignment = _linear(score, p25, 60, p75, 92)
    else:
        alignment = _linear(score, p75, 92, maximum, 100) if p75 < maximum else 100
    if p50 is None:
        rules.append(_rule("TEST2-005", "Median Not Reported", "P25 and P75 are present while P50 is absent", "Interpolate directly from P25 to P75; never infer a median.", {"p25": p25, "p75": p75}))
    alignment = round_internal(clamp(alignment))
    component = ComponentResult(name="testing_alignment", score=alignment, weight=1, weighted_value=alignment, status=EvaluationStatus.COMPLETE)
    return TestAlignmentEvaluationV2(rubric_version=V2_RUBRIC_VERSIONS["testing"], overall_score=alignment, display_score=round_display(alignment), components={"testing_alignment": component}, triggered_rules=tuple(rules), confidence=ConfidenceV2.from_score(100 if p50 is not None else 90), evaluation_date=request.evaluation_date, test_type=request.test_type, median_reported=p50 is not None)
