import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator

from api.admission_engine.engine.enums import CompletionStatus
from api.admission_engine.schemas.common import ApiModel


class AcademicTermWrite(ApiModel):
    term_order: int = Field(ge=0, le=30)
    term_name: str = Field(min_length=1, max_length=80)
    school_year: str = Field(min_length=1, max_length=20)
    average_grade: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    scale_min: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    scale_max: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)

    @model_validator(mode="after")
    def valid_scale(self) -> "AcademicTermWrite":
        if (
            self.scale_min is not None
            and self.scale_max is not None
            and self.scale_min >= self.scale_max
        ):
            raise ValueError("scale_max must be greater than scale_min")
        return self


class AcademicTermRead(AcademicTermWrite):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CourseWrite(ApiModel):
    term_id: uuid.UUID | None = None
    course_name: str = Field(min_length=1, max_length=160)
    subject_area: str | None = Field(default=None, max_length=80)
    course_level: str | None = Field(default=None, max_length=80)
    grade_value: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    grade_text: str | None = Field(default=None, max_length=40)
    is_advanced: bool | None = None
    is_highest_available: bool | None = None
    is_major_related: bool | None = None


class CourseRead(CourseWrite):
    id: uuid.UUID


class SchoolContextWrite(ApiModel):
    advanced_courses_available: int | None = Field(default=None, ge=0, le=100)
    advanced_program_types: list[str] | None = Field(default=None, max_length=30)
    highest_course_levels: dict[str, str] | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=2_000)

    @model_validator(mode="after")
    def validate_labels(self) -> "SchoolContextWrite":
        if self.advanced_program_types and any(len(value) > 80 for value in self.advanced_program_types):
            raise ValueError("advanced program labels may contain at most 80 characters")
        if self.highest_course_levels and any(
            len(key) > 80 or len(value) > 80 for key, value in self.highest_course_levels.items()
        ):
            raise ValueError("course-level keys and values may contain at most 80 characters")
        return self


class SchoolContextRead(SchoolContextWrite):
    id: uuid.UUID


class TestScoreWrite(ApiModel):
    test_type: str = Field(min_length=1, max_length=40)
    composite_score: Decimal | None = Field(
        default=None, ge=0, max_digits=8, decimal_places=2
    )
    section_scores: dict[str, Decimal] | None = Field(default=None, max_length=20)
    test_date: date | None = None
    is_official: bool | None = None


class TestScorePatch(ApiModel):
    test_type: str | None = Field(default=None, min_length=1, max_length=40)
    composite_score: Decimal | None = Field(
        default=None, ge=0, max_digits=8, decimal_places=2
    )
    section_scores: dict[str, Decimal] | None = Field(default=None, max_length=20)
    test_date: date | None = None
    is_official: bool | None = None


class TestScoreRead(TestScoreWrite):
    id: uuid.UUID
    created_at: datetime


class ActivityWrite(ApiModel):
    activity_order: int | None = Field(default=None, ge=0, le=50)
    activity_name: str = Field(min_length=1, max_length=160)
    position_title: str | None = Field(default=None, max_length=160)
    organization_name: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=2_000)
    category: str | None = Field(default=None, max_length=80)
    hours_per_week: Decimal | None = Field(default=None, ge=0, le=168)
    weeks_per_year: Decimal | None = Field(default=None, ge=0, le=53)
    start_date: date | None = None
    end_date: date | None = None
    duration_months: int | None = Field(default=None, ge=0, le=240)
    participant_count: int | None = Field(default=None, ge=0)
    people_impacted: int | None = Field(default=None, ge=0)
    leadership_level: Literal[
        "PARTICIPANT", "INFORMAL", "OPERATIONAL", "LEAD", "EXECUTIVE", "FOUNDER"
    ] | None = None
    recognition_scope: Literal[
        "NONE", "SCHOOL_LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"
    ] | None = None
    progression_level: int | None = Field(default=None, ge=0, le=3)
    is_founder: bool = False


class ActivityPatch(ApiModel):
    activity_order: int | None = Field(default=None, ge=0, le=50)
    activity_name: str | None = Field(default=None, min_length=1, max_length=160)
    position_title: str | None = Field(default=None, max_length=160)
    organization_name: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=2_000)
    category: str | None = Field(default=None, max_length=80)
    hours_per_week: Decimal | None = Field(default=None, ge=0, le=168)
    weeks_per_year: Decimal | None = Field(default=None, ge=0, le=53)
    start_date: date | None = None
    end_date: date | None = None
    duration_months: int | None = Field(default=None, ge=0, le=240)
    participant_count: int | None = Field(default=None, ge=0)
    people_impacted: int | None = Field(default=None, ge=0)
    leadership_level: Literal[
        "PARTICIPANT", "INFORMAL", "OPERATIONAL", "LEAD", "EXECUTIVE", "FOUNDER"
    ] | None = None
    recognition_scope: Literal[
        "NONE", "SCHOOL_LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"
    ] | None = None
    progression_level: int | None = Field(default=None, ge=0, le=3)
    is_founder: bool | None = None


class ActivityRead(ActivityWrite):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    current_score: int | None = Field(default=None, ge=0, le=100)


class HonorWrite(ApiModel):
    honor_name: str = Field(min_length=1, max_length=240)
    scope: Literal["SCHOOL", "LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"] | None = None
    placement: Literal[
        "PARTICIPANT", "HONORABLE_MENTION", "TOP_10", "TOP_5", "THIRD", "SECOND", "FIRST"
    ] | None = None
    participant_count: int | None = Field(default=None, ge=1)
    selection_rate: Decimal | None = Field(default=None, ge=0, le=1)
    organizer: str | None = Field(default=None, max_length=240)
    countries_represented: int | None = Field(default=None, ge=1)
    academic_area: str | None = Field(default=None, max_length=120)
    grade_received: str | None = Field(default=None, max_length=40)
    repeat_count: int = Field(default=1, ge=1, le=10)


class HonorPatch(ApiModel):
    honor_name: str | None = Field(default=None, min_length=1, max_length=240)
    scope: Literal["SCHOOL", "LOCAL", "REGIONAL", "STATE", "NATIONAL", "INTERNATIONAL"] | None = None
    placement: Literal[
        "PARTICIPANT", "HONORABLE_MENTION", "TOP_10", "TOP_5", "THIRD", "SECOND", "FIRST"
    ] | None = None
    participant_count: int | None = Field(default=None, ge=1)
    selection_rate: Decimal | None = Field(default=None, ge=0, le=1)
    organizer: str | None = Field(default=None, max_length=240)
    countries_represented: int | None = Field(default=None, ge=1)
    academic_area: str | None = Field(default=None, max_length=120)
    grade_received: str | None = Field(default=None, max_length=40)
    repeat_count: int | None = Field(default=None, ge=1, le=10)


class HonorRead(HonorWrite):
    id: uuid.UUID
    current_score: int | None = Field(default=None, ge=0, le=100)


class TargetWrite(ApiModel):
    college_id: uuid.UUID
    priority: int | None = Field(default=None, ge=1, le=100)
    application_round: str | None = Field(default=None, max_length=40)
    application_status: str | None = Field(default=None, max_length=40)


class TargetPatch(ApiModel):
    priority: int | None = Field(default=None, ge=1, le=100)
    application_round: str | None = Field(default=None, max_length=40)
    application_status: str | None = Field(default=None, max_length=40)


class TargetRead(TargetWrite):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TargetWithCollege(TargetRead):
    college_name: str
    college_slug: str


class MaterialStatusWrite(ApiModel):
    requirement_type: str = Field(min_length=1, max_length=80)
    completion_status: CompletionStatus
    linked_entity_id: uuid.UUID | None = None
    notes: str | None = Field(default=None, max_length=1_000)


class MaterialStatusRead(MaterialStatusWrite):
    id: uuid.UUID
    updated_at: datetime


class EvaluationRead(ApiModel):
    id: uuid.UUID
    evaluation_type: str
    college_id: uuid.UUID | None
    engine_version: str
    rubric_version: str
    overall_score: Decimal | None
    display_score: int | None
    confidence: str
    status: str
    evaluation_date: date
    evaluated_at: datetime
