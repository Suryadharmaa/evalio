import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from api.admission_engine.schemas.common import ApiModel

EssayType = Literal["COMMON_APP", "SUPPLEMENTAL", "SCHOLARSHIP", "OTHER"]


class EssayEvaluationRequest(ApiModel):
    essay_type: EssayType = "COMMON_APP"
    text: str = Field(min_length=1, max_length=100_000)
    min_words: int | None = Field(default=250, ge=0, le=10_000)
    word_limit: int | None = Field(default=650, ge=1, le=10_000)
    prompt_text: str | None = Field(default=None, max_length=10_000)
    title: str | None = Field(default=None, max_length=240)
    save: bool = False
    save_raw_text: bool = False

    @model_validator(mode="after")
    def validate_limits(self) -> "EssayEvaluationRequest":
        if (
            self.min_words is not None
            and self.word_limit is not None
            and self.min_words > self.word_limit
        ):
            raise ValueError("min_words cannot exceed word_limit")
        return self


class EssayMetrics(ApiModel):
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    average_sentence_length: float
    median_sentence_length: float
    sentence_length_stddev: float
    flesch_reading_ease: float | None
    lexical_diversity: float | None
    specificity_density: float
    reflection_density: float


class EssayIssue(ApiModel):
    rule_id: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    title: str
    message: str
    evidence: dict[str, object] = Field(default_factory=dict)
    score_delta: float | None = None


class EssayEvaluationResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "essay-1.0.0"
    overall_score: float
    display_score: int
    label: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    components: dict[str, float]
    metrics: EssayMetrics
    issues: list[EssayIssue]
    triggered_rules: list[str]


class SavedEssayCreate(EssayEvaluationRequest):
    pass


class SavedEssayRead(ApiModel):
    id: uuid.UUID
    profile_id: uuid.UUID | None
    essay_type: str
    title: str | None
    prompt_text: str | None
    word_limit: int | None
    min_words: int | None
    raw_text: str | None
    save_raw_text: bool
    content_hash: str
    created_at: datetime
    updated_at: datetime


class SavedEssayHistoryItem(SavedEssayRead):
    evaluation_id: uuid.UUID | None = None
    display_score: int | None = None
    confidence: str | None = None


class SavedEssayCompareRequest(ApiModel):
    left_evaluation_id: uuid.UUID
    right_evaluation_id: uuid.UUID

    @model_validator(mode="after")
    def require_distinct_evaluations(self) -> "SavedEssayCompareRequest":
        if self.left_evaluation_id == self.right_evaluation_id:
            raise ValueError("saved comparisons require two distinct evaluations")
        return self
