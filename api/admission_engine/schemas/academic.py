from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator

from api.admission_engine.schemas.common import ApiModel


class AcademicTermInput(ApiModel):
    term_order: int = Field(ge=0, le=30)
    average_grade: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)


class CourseInput(ApiModel):
    grade_value: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    is_major_related: bool = False


class RigorEvidence(ApiModel):
    highest_level_core_areas: int = Field(ge=0, le=5)
    relevant_core_areas: int = Field(ge=0, le=5)
    core_coverage: Literal["ALL", "MINOR_GAP", "MAJOR_GAP", "MULTIPLE_GAPS"]
    advanced_taken: int = Field(ge=0, le=100)
    advanced_opportunities: int = Field(ge=0, le=100)
    progression: Literal["INCREASING", "STABLE", "MIXED", "DECLINING"]
    major_preparation: Literal["STRONG", "ADEQUATE", "LIMITED", "MISSING"]

    @model_validator(mode="after")
    def validate_counts(self) -> "RigorEvidence":
        if self.highest_level_core_areas > self.relevant_core_areas:
            raise ValueError("highest_level_core_areas cannot exceed relevant_core_areas")
        if self.advanced_taken > self.advanced_opportunities:
            raise ValueError("advanced_taken cannot exceed advanced_opportunities")
        return self


class AcademicEvaluationRequest(ApiModel):
    terms: list[AcademicTermInput] = Field(min_length=1, max_length=30)
    courses: list[CourseInput] = Field(default_factory=list, max_length=200)
    scale_min: float | None = None
    scale_max: float | None = None
    class_rank: int | None = Field(default=None, ge=1)
    class_size: int | None = Field(default=None, ge=1)
    academic_context_score: float | None = Field(default=None, ge=0, le=100)
    rigor_evidence: RigorEvidence | None = None

    @model_validator(mode="after")
    def validate_ranges(self) -> "AcademicEvaluationRequest":
        if (
            self.scale_min is not None
            and self.scale_max is not None
            and self.scale_min >= self.scale_max
        ):
            raise ValueError("scale_max must be greater than scale_min")
        if (
            self.class_rank is not None
            and self.class_size is not None
            and self.class_rank > self.class_size
        ):
            raise ValueError("class_rank cannot exceed class_size")
        return self


class RigorScores(ApiModel):
    challenge: int
    core_coverage: int
    advanced_utilization: int
    progression: int
    major_preparation: int
    total: int = Field(ge=0, le=100)


class AcademicScores(ApiModel):
    performance: float | None
    rigor: float | None
    trend: float | None
    context: float | None
    major_preparation: float | None


class AcademicEvaluationResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "academic-1.1.0"
    overall_score: float | None
    display_score: int | None
    components: AcademicScores
    rigor_details: RigorScores | None
    trend_slope: float | None
    triggered_rules: list[dict[str, object]] = Field(default_factory=list)
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = "HIGH"
