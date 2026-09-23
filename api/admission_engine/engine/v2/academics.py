from datetime import date
from itertools import combinations
from statistics import fmean, median

from pydantic import Field, model_validator

from api.admission_engine.config import V2_RUBRIC_VERSIONS
from api.admission_engine.engine.enums import ConfidenceLevel, EvaluationStatus, RuleSeverity
from api.admission_engine.engine.models import ComponentResult, StrictModel
from api.admission_engine.engine.scoring import (
    clamp,
    round_display,
    round_internal,
    weighted_result,
)
from api.admission_engine.engine.v2.models import (
    ConfidenceV2,
    NumericEvaluationV2,
    RuleResultV2,
    StatusEvaluationV2,
)

ACADEMIC_V2_WEIGHTS = {"achievement": 0.55, "course_rigor": 0.35, "trend": 0.10}
_NATIVE_ANCHORS = [(0.0, 20.0), (0.60, 58.0), (0.65, 64.0), (0.70, 70.0), (0.75, 76.0), (0.80, 82.0), (0.85, 88.0), (0.90, 94.0), (0.95, 100.0)]
_RANK_ANCHORS = [(0.01, 100.0), (0.05, 96.0), (0.10, 92.0), (0.20, 86.0), (0.30, 80.0), (0.50, 70.0), (1.0, 40.0)]


class AcademicTermV2(StrictModel):
    term_order: int = Field(ge=0, le=30)
    average_grade: float


class AcademicRequestV2(StrictModel):
    terms: tuple[AcademicTermV2, ...] = ()
    scale_min: float | None = None
    scale_max: float | None = None
    grading_system: str = "NATIVE"
    documented_conversion_selected: bool = False
    class_rank: int | None = Field(default=None, ge=1)
    class_size: int | None = Field(default=None, ge=1)
    rank_not_published: bool = False
    course_rigor_score: float | None = Field(default=None, ge=0, le=100)
    evaluation_date: date

    @model_validator(mode="after")
    def validate_context(self) -> "AcademicRequestV2":
        if (self.scale_min is None) != (self.scale_max is None):
            raise ValueError("scale_min and scale_max must be provided together")
        if self.scale_min is not None and self.scale_max is not None:
            if self.scale_min >= self.scale_max:
                raise ValueError("scale_max must be greater than scale_min")
            if any(not self.scale_min <= term.average_grade <= self.scale_max for term in self.terms):
                raise ValueError("term grade must be within native scale bounds")
        if (self.class_rank is None) != (self.class_size is None):
            raise ValueError("class_rank and class_size must be provided together")
        if self.class_rank is not None and self.class_size is not None and self.class_rank > self.class_size:
            raise ValueError("class_rank cannot exceed class_size")
        return self


class AcademicEvaluationV2(NumericEvaluationV2):
    achievement_score: float | None
    native_performance_score: float | None
    rank_evidence_score: float | None
    trend_slope: float | None
    effective_weights: dict[str, float]


def _interpolate(value: float, anchors: list[tuple[float, float]]) -> float:
    if value <= anchors[0][0]:
        return anchors[0][1]
    if value >= anchors[-1][0]:
        return anchors[-1][1]
    for (left_x, left_y), (right_x, right_y) in zip(anchors, anchors[1:], strict=True):
        if left_x <= value <= right_x:
            ratio = (value - left_x) / (right_x - left_x)
            return left_y + ratio * (right_y - left_y)
    raise AssertionError("unreachable interpolation interval")


def native_performance(request: AcademicRequestV2) -> float | None:
    if not request.terms or request.scale_min is None or request.scale_max is None:
        return None
    average = fmean(term.average_grade for term in request.terms)
    position = (average - request.scale_min) / (request.scale_max - request.scale_min)
    return round_internal(_interpolate(clamp(position, 0, 1), _NATIVE_ANCHORS))


def rank_evidence(rank: int | None, class_size: int | None) -> float | None:
    if rank is None or class_size is None:
        return None
    return round_internal(_interpolate(rank / class_size, _RANK_ANCHORS))


def theil_sen_trend(request: AcademicRequestV2) -> tuple[float | None, float | None]:
    if request.scale_min is None or request.scale_max is None:
        return None, None
    terms = sorted(request.terms, key=lambda term: term.term_order)
    if len(terms) < 2:
        return None, None
    scale_span = request.scale_max - request.scale_min
    points = [(term.term_order, (term.average_grade - request.scale_min) / scale_span * 100) for term in terms]
    slopes = [(right_y - left_y) / (right_x - left_x) for (left_x, left_y), (right_x, right_y) in combinations(points, 2) if right_x != left_x]
    if not slopes:
        return None, None
    slope = round(median(slopes), 4)
    score = 95 if slope >= 1.5 else 88 if slope >= 0.75 else 80 if slope >= 0.25 else 75 if slope >= -0.24 else 65 if slope > -0.75 else 52 if slope > -1.5 else 35
    return float(score), slope


def _rule(rule_id: str, title: str, trigger: str, effect: str, evidence: dict[str, object], severity: RuleSeverity = RuleSeverity.INFO) -> RuleResultV2:
    return RuleResultV2(rule_id=rule_id, domain="ACADEMIC", category="Academic Strength", severity=severity, title=title, trigger=trigger, evidence=evidence, effect=effect, message=effect, confidence=ConfidenceLevel.HIGH, methodology_ref="SCORING_SPEC_V2.md#part-a--academics")


def evaluate_academic_v2(request: AcademicRequestV2) -> AcademicEvaluationV2 | StatusEvaluationV2:
    rules: list[RuleResultV2] = []
    native = native_performance(request)
    rank = rank_evidence(request.class_rank, request.class_size)
    if request.grading_system != "US_4_0" and not request.documented_conversion_selected:
        rules.append(_rule("ACAD2-001", "Native Scale Required", "Non-US/native grading without selected conversion", "Evaluate on the documented native scale; do not auto-convert to 4.0.", {"grading_system": request.grading_system}))
    if native is None:
        rules.append(_rule("ACAD2-002", "Missing Scale Bounds", "Native performance cannot be normalized", "Academic Achievement is N/A.", {}, RuleSeverity.HIGH))
    if rank is not None:
        rules.append(_rule("ACAD2-003", "Rank Evidence Available", "Valid rank and cohort size supplied", "Rank corroborates 20% of Academic Achievement.", {"rank": request.class_rank, "class_size": request.class_size}))
    elif request.rank_not_published:
        rules.append(_rule("ACAD2-004", "Rank Not Published", "School does not publish rank", "Rank is excluded with no penalty.", {}))
    achievement = None if native is None else round_internal(native * 0.8 + rank * 0.2) if rank is not None else native
    trend, slope = theil_sen_trend(request)
    if trend is None:
        rules.append(_rule("ACAD2-007", "Insufficient Trend History", "Fewer than two valid chronological terms", "Trend is N/A and its weight is redistributed.", {"term_count": len(request.terms)}))
    elif slope is not None and slope >= 0.75:
        rules.append(_rule("ACAD2-005", "Positive Robust Trend", "Theil-Sen slope is at least +0.75", "Positive trend anchor applies.", {"slope": slope}))
    elif slope is not None and slope <= -0.75:
        rules.append(_rule("ACAD2-006", "Negative Robust Trend", "Theil-Sen slope is at most -0.75", "Negative trend anchor applies.", {"slope": slope}, RuleSeverity.MEDIUM))
    values = {"achievement": achievement, "course_rigor": request.course_rigor_score, "trend": trend}
    weighted = weighted_result(values, ACADEMIC_V2_WEIGHTS)
    available = sum(value is not None for value in values.values())
    confidence = ConfidenceV2.from_score(100 if available == 3 else 80 if available == 2 else 60 if available == 1 else 0)
    if weighted.score is None:
        return StatusEvaluationV2(rubric_version=V2_RUBRIC_VERSIONS["academic"], status="INSUFFICIENT_DATA", evidence={"available_components": available}, triggered_rules=tuple(rules), confidence=confidence, evaluation_date=request.evaluation_date)
    components = {name: ComponentResult(name=name, score=value, weight=weighted.effective_weights.get(name), weighted_value=None if value is None else round_internal(value * weighted.effective_weights[name]), status=EvaluationStatus.COMPLETE if value is not None else EvaluationStatus.NOT_APPLICABLE) for name, value in values.items()}
    return AcademicEvaluationV2(rubric_version=V2_RUBRIC_VERSIONS["academic"], overall_score=weighted.score, display_score=round_display(weighted.score), components=components, triggered_rules=tuple(rules), confidence=confidence, evaluation_date=request.evaluation_date, achievement_score=achievement, native_performance_score=native, rank_evidence_score=rank, trend_slope=slope, effective_weights=weighted.effective_weights)
