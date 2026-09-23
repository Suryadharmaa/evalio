from typing import Literal

from pydantic import Field

from api.admission_engine.schemas.common import ApiModel

PatternRisk = Literal["LOW", "MODERATE", "HIGH"]
PatternLevel = Literal["NORMAL", "LOW", "MEDIUM", "HIGH", "INSUFFICIENT_DATA"]
PatternCategory = Literal["RHYTHM", "DETAIL", "LANGUAGE", "STANCE"]


class WritingPatternRequest(ApiModel):
    text: str = Field(min_length=1, max_length=100_000)


class WritingPatternSignal(ApiModel):
    signal_id: str
    label: str
    category: PatternCategory
    metric: str
    observed_value: float | int | str
    threshold: str
    triggered: bool
    level: PatternLevel
    evidence: list[str] = Field(default_factory=list)
    explanation: str


class WritingPatternResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "writing-patterns-1.0.0"
    risk: PatternRisk
    triggered_count: int
    total_signals: int
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    signals: list[WritingPatternSignal]
