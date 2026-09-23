from typing import Literal

from pydantic import Field

from api.admission_engine.schemas.common import ApiModel


class ProfileStrengthRequest(ApiModel):
    academics: float | None = Field(default=None, ge=0, le=100)
    activities: float | None = Field(default=None, ge=0, le=100)
    honors: float | None = Field(default=None, ge=0, le=100)
    essay_signals: float | None = Field(default=None, ge=0, le=100)
    lor_signals: float | None = Field(default=None, ge=0, le=100)
    testing: float | None = Field(default=None, ge=0, le=100)


class ProfileStrengthResponse(ApiModel):
    score: float | None
    display_score: int | None
    components: dict[str, float | None]
    effective_weights: dict[str, float]
    disclaimer: Literal[
        "This is not college-specific, an admission probability, or an official score."
    ] = "This is not college-specific, an admission probability, or an official score."
