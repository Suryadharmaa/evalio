from typing import Literal

from pydantic import Field

from api.admission_engine.schemas.common import ApiModel


class ActivityInput(ApiModel):
    activity_name: str = Field(min_length=1, max_length=160)
    people_impacted: int | None = Field(default=None, ge=0)
    impact_level: Literal["NONE", "SELF", "SMALL_GROUP", "VERIFIABLE_EXCEPTIONAL"] = "NONE"
    leadership_level: Literal[
        "PARTICIPANT", "INFORMAL", "OPERATIONAL", "LEAD", "EXECUTIVE", "FOUNDER"
    ] = "PARTICIPANT"
    founder_responsibility_evidence: bool = False
    sustained_operations: bool = False
    duration_months: int = Field(ge=0, le=240)
    initiative_level: Literal[
        "ASSIGNED", "OCCASIONAL", "IMPROVED", "STARTED_PROJECT", "CREATED_PROGRAM"
    ] = "ASSIGNED"
    hours_per_week: float = Field(ge=0, le=168)
    recognition_scope: Literal[
        "NONE", "SCHOOL_LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"
    ] = "NONE"
    progression_level: Literal["NONE", "SOME", "CLEAR", "MULTIPLE"] = "NONE"


class ActivityScores(ApiModel):
    impact: int
    leadership: int
    duration: int
    initiative: int
    time_commitment: int
    recognition: int
    progression: int
    total: int = Field(ge=0, le=100)


class ActivityEvaluationRequest(ApiModel):
    activities: list[ActivityInput] = Field(min_length=1, max_length=50)


class ActivityEvaluationResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "activity-1.1.0"
    individual_scores: list[ActivityScores]
    portfolio_score: float
    display_score: int
    warnings: list[str] = Field(default_factory=list)
    confidence: Literal["HIGH"] = "HIGH"


class ActivityDescriptionRequest(ApiModel):
    position_title: str = Field(default="", max_length=100)
    organization: str = Field(default="", max_length=160)
    description: str = Field(min_length=1, max_length=2_000)
    character_limit: int = Field(default=150, ge=1, le=2_000)


class ActivityDescriptionResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "activity-description-1.0.0"
    overall_score: float
    display_score: int
    components: dict[str, int]
    triggered_rules: list[str]
    confidence: Literal["HIGH", "MEDIUM"] = "HIGH"
