from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.admission_engine.engine.enums import (
    ConfidenceLevel,
    EvaluationStatus,
    RuleDomain,
    RuleSeverity,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RuleResult(StrictModel):
    rule_id: str = Field(pattern=r"^[A-Z][A-Z0-9]*-\d{3}$")
    rule_version: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=160)
    domain: RuleDomain
    category: str = Field(min_length=1, max_length=80)
    severity: RuleSeverity
    message: str = Field(min_length=1, max_length=1_000)
    evidence: dict[str, Any] = Field(default_factory=dict)
    score_delta: float | None = None
    confidence: ConfidenceLevel
    actionable: bool = True
    textual_position: int | None = Field(default=None, ge=0)

    @field_validator("score_delta")
    @classmethod
    def score_delta_must_be_finite(cls, value: float | None) -> float | None:
        if value is not None and (value != value or value in (float("inf"), float("-inf"))):
            raise ValueError("score_delta must be finite")
        return value


class ComponentResult(StrictModel):
    name: str
    score: float | None = Field(default=None, ge=0, le=100)
    weight: float | None = Field(default=None, ge=0, le=1)
    weighted_value: float | None = None
    status: EvaluationStatus = EvaluationStatus.COMPLETE


class EvaluationResult(StrictModel):
    engine_version: str
    rubric_version: str
    overall_score: float | None = Field(default=None, ge=0, le=100)
    display_score: int | None = Field(default=None, ge=0, le=100)
    components: dict[str, ComponentResult] = Field(default_factory=dict)
    triggered_rules: tuple[RuleResult, ...] = ()
    metrics: dict[str, Any] = Field(default_factory=dict)
    confidence: ConfidenceLevel
    status: EvaluationStatus = EvaluationStatus.COMPLETE
    input_hash: str = Field(min_length=64, max_length=64)
    evaluation_date: date
    evaluated_at: datetime
