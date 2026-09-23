from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from api.admission_engine.config import V2_RUBRIC_VERSIONS
from api.admission_engine.engine.enums import ConfidenceLevel, EvaluationStatus, RuleSeverity
from api.admission_engine.engine.models import ComponentResult, StrictModel
from api.admission_engine.engine.scoring import round_display, round_internal, weighted_result
from api.admission_engine.engine.v2.models import ConfidenceV2, NumericEvaluationV2, RuleResultV2

COURSEWORK_V2_WEIGHTS = {"challenge": 0.55, "core_coverage": 0.20, "advanced_utilization": 0.15, "progression": 0.10}
MajorPreparation = Literal["STRONG", "ADEQUATE", "LIMITED", "GAP", "N/A"]


class CourseworkRequestV2(StrictModel):
    relevant_areas: int = Field(ge=1, le=20)
    highest_level_areas: int = Field(ge=0, le=20)
    core_coverage: Literal["ALL", "MINOR_GAP", "MAJOR_GAP", "MULTIPLE_MAJOR_GAPS"]
    advanced_opportunities: int | None = Field(default=None, ge=0, le=100)
    advanced_taken: int = Field(default=0, ge=0, le=100)
    progression: Literal["INCREASING", "STABLE", "MIXED", "DECLINING"]
    prerequisite_map_configured: bool = False
    prerequisites_met: int | None = Field(default=None, ge=0)
    prerequisites_total: int | None = Field(default=None, ge=1)
    evaluation_date: date

    @model_validator(mode="after")
    def validate_counts(self) -> "CourseworkRequestV2":
        if self.highest_level_areas > self.relevant_areas:
            raise ValueError("highest_level_areas cannot exceed relevant_areas")
        if self.advanced_opportunities is not None and self.advanced_taken > self.advanced_opportunities:
            raise ValueError("advanced_taken cannot exceed advanced_opportunities")
        if self.prerequisite_map_configured:
            if self.prerequisites_met is None or self.prerequisites_total is None:
                raise ValueError("configured prerequisites require met and total counts")
            if self.prerequisites_met > self.prerequisites_total:
                raise ValueError("prerequisites_met cannot exceed prerequisites_total")
        return self


class CourseworkEvaluationV2(NumericEvaluationV2):
    major_preparation: MajorPreparation
    effective_weights: dict[str, float]


def _rule(rule_id: str, title: str, trigger: str, effect: str, evidence: dict[str, object], severity: RuleSeverity = RuleSeverity.INFO) -> RuleResultV2:
    return RuleResultV2(rule_id=rule_id, domain="COURSEWORK", category="Course Rigor", severity=severity, title=title, trigger=trigger, evidence=evidence, effect=effect, message=effect, confidence=ConfidenceLevel.HIGH, methodology_ref="SCORING_SPEC_V2.md#part-b--coursework")


def _major_preparation(request: CourseworkRequestV2) -> MajorPreparation:
    if not request.prerequisite_map_configured or request.prerequisites_total is None or request.prerequisites_met is None:
        return "N/A"
    ratio = request.prerequisites_met / request.prerequisites_total
    return "STRONG" if ratio == 1 else "ADEQUATE" if ratio >= 0.75 else "LIMITED" if ratio > 0 else "GAP"


def evaluate_coursework_v2(request: CourseworkRequestV2) -> CourseworkEvaluationV2:
    ratio = request.highest_level_areas / request.relevant_areas
    challenge = 95 if ratio >= 0.8 else 85 if ratio >= 0.6 else 72 if ratio >= 0.4 else 58 if ratio >= 0.2 else 42
    coverage = {"ALL": 95, "MINOR_GAP": 80, "MAJOR_GAP": 60, "MULTIPLE_MAJOR_GAPS": 35}[request.core_coverage]
    rules: list[RuleResultV2] = []
    advanced: float | None
    if request.advanced_opportunities is None:
        advanced = None
        rules.append(_rule("RIGOR2-002", "Opportunity Context Missing", "Advanced-course availability is unknown", "Do not assume low utilization; reduce confidence.", {}, RuleSeverity.MEDIUM))
    elif request.advanced_opportunities == 0:
        advanced = None
        rules.append(_rule("RIGOR2-001", "No Advanced Courses Available", "School reports zero relevant advanced opportunities", "Advanced Opportunity Use is N/A and its weight is redistributed.", {}))
    else:
        utilization = request.advanced_taken / request.advanced_opportunities
        advanced = float(95 if utilization >= 0.8 else 85 if utilization >= 0.6 else 70 if utilization >= 0.4 else 55 if utilization >= 0.2 else 40 if utilization > 0 else 25)
        if utilization >= 0.8:
            rules.append(_rule("RIGOR2-003", "High Opportunity Utilization", "Advanced utilization is at least 80%", "Advanced Opportunity Use is 95.", {"utilization": round_internal(utilization, 4)}))
    progression = float({"INCREASING": 95, "STABLE": 80, "MIXED": 65, "DECLINING": 40}[request.progression])
    major = _major_preparation(request)
    if request.core_coverage != "ALL":
        rules.append(_rule("RIGOR2-004", "Core Academic Gap", "Expected core coverage is incomplete", "Core Academic Coverage is reduced according to the documented gap.", {"coverage": request.core_coverage}, RuleSeverity.HIGH if request.core_coverage == "MULTIPLE_MAJOR_GAPS" else RuleSeverity.MEDIUM))
    if major == "GAP":
        rules.append(_rule("RIGOR2-005", "Major Preparation Gap", "Configured program prerequisites are unmet", "Major Preparation is GAP; general Course Rigor is unchanged.", {}, RuleSeverity.HIGH))
    values = {"challenge": float(challenge), "core_coverage": float(coverage), "advanced_utilization": advanced, "progression": progression}
    weighted = weighted_result(values, COURSEWORK_V2_WEIGHTS)
    assert weighted.score is not None
    confidence = ConfidenceV2.from_score(75 if request.advanced_opportunities is None else 100)
    components = {name: ComponentResult(name=name, score=value, weight=weighted.effective_weights.get(name), weighted_value=None if value is None else round_internal(value * weighted.effective_weights[name]), status=EvaluationStatus.COMPLETE if value is not None else EvaluationStatus.NOT_APPLICABLE) for name, value in values.items()}
    return CourseworkEvaluationV2(rubric_version=V2_RUBRIC_VERSIONS["coursework"], overall_score=weighted.score, display_score=round_display(weighted.score), components=components, triggered_rules=tuple(rules), confidence=confidence, evaluation_date=request.evaluation_date, major_preparation=major, effective_weights=weighted.effective_weights)
