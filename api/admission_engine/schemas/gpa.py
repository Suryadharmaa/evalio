import math
from typing import Literal

from pydantic import Field, model_validator

from api.admission_engine.schemas.common import ApiModel

CourseLevel = Literal["REGULAR", "HONORS", "AP", "IB", "DUAL_ENROLLMENT", "OTHER_ADVANCED"]
LetterGrade = Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]
WeightingMethod = Literal["NONE", "HONORS_0_5_ADVANCED_1_0", "CUSTOM"]


class GpaCourse(ApiModel):
    course: str = Field(min_length=1, max_length=160)
    grade: LetterGrade
    course_level: CourseLevel = "REGULAR"
    credits: float = Field(gt=0, le=20, allow_inf_nan=False)


class InternationalGrade(ApiModel):
    label: str = Field(min_length=1, max_length=160)
    value: float = Field(allow_inf_nan=False)
    weight: float = Field(default=1, gt=0, le=100, allow_inf_nan=False)


class GpaCalculationRequest(ApiModel):
    mode: Literal["US_COURSES", "INTERNATIONAL_RAW"]
    courses: list[GpaCourse] = Field(default_factory=list, max_length=100)
    weighting_method: WeightingMethod = "NONE"
    custom_offsets: dict[CourseLevel, float] | None = None
    curriculum_name: str | None = Field(default=None, max_length=160)
    scale_min: float | None = Field(default=None, allow_inf_nan=False)
    scale_max: float | None = Field(default=None, allow_inf_nan=False)
    international_grades: list[InternationalGrade] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def validate_mode(self) -> "GpaCalculationRequest":
        if self.mode == "US_COURSES":
            if not self.courses:
                raise ValueError("add at least one US course")
            if self.weighting_method == "CUSTOM" and self.custom_offsets is None:
                raise ValueError("custom_offsets are required for CUSTOM weighting")
            if self.custom_offsets and any(not math.isfinite(value) or value < 0 or value > 5 for value in self.custom_offsets.values()):
                raise ValueError("custom weighting offsets must be between 0 and 5")
        else:
            if not self.curriculum_name or not self.curriculum_name.strip():
                raise ValueError("curriculum_name is required for international mode")
            if self.scale_min is None or self.scale_max is None or self.scale_max <= self.scale_min:
                raise ValueError("scale_max must be greater than scale_min")
            if not self.international_grades:
                raise ValueError("add at least one international grade")
            if any(item.value < self.scale_min or item.value > self.scale_max for item in self.international_grades):
                raise ValueError("international grades must be within the selected scale")
        return self


class GpaCourseResult(ApiModel):
    label: str
    credits_or_weight: float
    base_value: float
    weighted_value: float | None = None
    course_level: CourseLevel | None = None


class GpaCalculationResponse(ApiModel):
    calculator_version: str = "gpa-calculator-1.0.0"
    mode: Literal["US_COURSES", "INTERNATIONAL_RAW"]
    unweighted_gpa: float | None = None
    weighted_gpa: float | None = None
    academic_average: float | None = None
    scale_min: float | None = None
    scale_max: float | None = None
    total_credits_or_weight: float
    conversion: Literal["NOT_APPLIED"]
    weighting_method: WeightingMethod | None = None
    formula: list[str]
    breakdown: list[GpaCourseResult]
