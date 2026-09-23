from datetime import date
from typing import Any

from pydantic import Field, model_validator

from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.engine.enums import ConfidenceLevel, EvaluationStatus, RuleSeverity
from api.admission_engine.engine.models import ComponentResult, StrictModel
from api.admission_engine.engine.scoring import round_display, round_internal


class ConfidenceV2(StrictModel):
    score: float = Field(ge=0, le=100)
    band: ConfidenceLevel

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceV2":
        normalized = round_internal(score)
        band = ConfidenceLevel.HIGH if normalized >= 85 else ConfidenceLevel.MEDIUM if normalized >= 65 else ConfidenceLevel.LOW
        return cls(score=normalized, band=band)


class RuleResultV2(StrictModel):
    rule_id: str = Field(pattern=r"^[A-Z][A-Z0-9]*-\d{3}$")
    rule_version: str = "2.0.0"
    domain: str = Field(min_length=1)
    category: str = Field(min_length=1)
    severity: RuleSeverity
    title: str = Field(min_length=1)
    trigger: str = Field(min_length=1)
    evidence: dict[str, Any] = Field(default_factory=dict)
    effect: str = Field(min_length=1)
    message: str = Field(min_length=1)
    confidence: ConfidenceLevel
    methodology_ref: str = Field(min_length=1)


class NumericEvaluationV2(StrictModel):
    engine_version: str = ENGINE_VERSION
    rubric_version: str = Field(pattern=r"^[a-z-]+-2\.\d+\.\d+$")
    overall_score: float = Field(ge=0, le=100)
    display_score: int = Field(ge=0, le=100)
    components: dict[str, ComponentResult] = Field(default_factory=dict)
    signals: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    triggered_rules: tuple[RuleResultV2, ...] = ()
    confidence: ConfidenceV2
    status: EvaluationStatus = EvaluationStatus.COMPLETE
    evaluation_date: date

    @model_validator(mode="after")
    def score_rounding_is_consistent(self) -> "NumericEvaluationV2":
        internal = round_internal(self.overall_score)
        if self.overall_score != internal or self.display_score != round_display(internal):
            raise ValueError("V2 internal/display scores must use canonical rounding")
        return self


class StatusEvaluationV2(StrictModel):
    engine_version: str = ENGINE_VERSION
    rubric_version: str = Field(pattern=r"^[a-z-]+-2\.\d+\.\d+$")
    status: str = Field(min_length=1, max_length=80)
    evidence: dict[str, Any] = Field(default_factory=dict)
    signals: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    triggered_rules: tuple[RuleResultV2, ...] = ()
    confidence: ConfidenceV2
    evaluation_date: date
