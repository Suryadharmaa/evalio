from typing import Literal

from pydantic import Field

from api.admission_engine.schemas.common import ApiModel


class HonorInput(ApiModel):
    honor_name: str = Field(min_length=1, max_length=240)
    scope: Literal["SCHOOL", "LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"] | None = (
        None
    )
    selection_rate: float | None = Field(default=None, ge=0, le=1)
    placement: Literal[
        "PARTICIPANT", "HONORABLE_MENTION", "TOP_10", "TOP_5", "THIRD", "SECOND", "FIRST"
    ]
    academic_relevance: int = Field(ge=0, le=15)
    repeat_count: int = Field(default=1, ge=1, le=10)
    organizer: str | None = Field(default=None, max_length=240)
    countries_represented: int | None = Field(default=None, ge=1)


class HonorScore(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "honor-1.1.0"
    scope: int | None
    selectivity: int
    placement: int
    academic_relevance: int
    recurrence: int
    overall_score: float
    display_score: int
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    triggered_rules: list[str] = Field(default_factory=list)
