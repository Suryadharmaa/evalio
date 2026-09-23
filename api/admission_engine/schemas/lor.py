import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from api.admission_engine.schemas.common import ApiModel


class LorEvaluationRequest(ApiModel):
    text: str = Field(min_length=1, max_length=100_000)
    recommender_role: str | None = Field(default=None, max_length=160)
    relationship_duration_months: int | None = Field(default=None, ge=0, le=600)
    instructional_context: str | None = Field(default=None, max_length=500)
    save: bool = False


class LorEvaluationResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "lor-1.0.0"
    overall_score: float
    display_score: int
    components: dict[str, float]
    triggered_rules: list[str]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]


class SavedRecommendationCreate(LorEvaluationRequest):
    save_raw_text: bool = False


class SavedRecommendationRead(ApiModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    recommender_role: str | None
    relationship_duration_months: int | None
    raw_text: str | None
    save_raw_text: bool
    content_hash: str
    created_at: datetime
