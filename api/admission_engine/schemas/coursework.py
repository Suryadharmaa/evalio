from typing import Literal

from pydantic import Field, field_validator, model_validator

from api.admission_engine.schemas.common import ApiModel

CoreArea = Literal["ENGLISH", "MATHEMATICS", "LAB_SCIENCE", "SOCIAL_SCIENCE", "FOREIGN_LANGUAGE", "OTHER"]
CourseLevel = Literal["STANDARD", "HONORS", "AP", "IB_SL", "IB_HL", "A_LEVEL", "DUAL_ENROLLMENT", "OTHER_ADVANCED"]
CourseworkComponentKey = Literal["challenge", "core_coverage", "advanced_utilization", "progression", "major_preparation"]
CourseworkRating = Literal["STRONG", "SOLID", "MODERATE", "LIMITED"]
CourseworkConfidence = Literal["HIGH", "MEDIUM", "LOW"]


class CourseworkCourse(ApiModel):
    course: str = Field(min_length=1, max_length=160)
    subject_area: CoreArea
    grade_level: int = Field(ge=1, le=13)
    course_level: CourseLevel
    is_major_related: bool = False

    @field_validator("course")
    @classmethod
    def normalize_course(cls, value: str) -> str:
        clean = " ".join(value.split())
        if not clean:
            raise ValueError("course name cannot be blank")
        return clean


class CourseworkEvaluationRequest(ApiModel):
    curriculum_type: str = Field(min_length=1, max_length=100)
    grade_levels: list[int] = Field(min_length=1, max_length=13)
    courses: list[CourseworkCourse] = Field(min_length=1, max_length=100)
    advanced_courses_available: int = Field(ge=0, le=100)
    advanced_program_types: list[str] = Field(default_factory=list, max_length=20)
    highest_levels_available: dict[CoreArea, CourseLevel] = Field(default_factory=dict)
    intended_major: str = Field(min_length=1, max_length=160)
    school_context_notes: str | None = Field(default=None, max_length=2_000)

    @field_validator("curriculum_type", "intended_major")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        clean = " ".join(value.split())
        if not clean:
            raise ValueError("value cannot be blank")
        return clean

    @field_validator("school_context_notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        clean = " ".join(value.split()) if value else ""
        return clean or None

    @field_validator("grade_levels")
    @classmethod
    def unique_grade_levels(cls, values: list[int]) -> list[int]:
        return sorted(set(values))

    @field_validator("advanced_program_types")
    @classmethod
    def normalize_programs(cls, values: list[str]) -> list[str]:
        clean = list(dict.fromkeys(" ".join(value.split()) for value in values if value.strip()))
        if any(len(value) > 80 for value in clean):
            raise ValueError("advanced program names may contain at most 80 characters")
        return clean

    @model_validator(mode="after")
    def validate_context(self) -> "CourseworkEvaluationRequest":
        submitted_levels = set(self.grade_levels)
        if any(course.grade_level not in submitted_levels for course in self.courses):
            raise ValueError("every course grade_level must be included in grade_levels")
        advanced_taken = sum(course.course_level != "STANDARD" for course in self.courses)
        if advanced_taken > self.advanced_courses_available:
            raise ValueError("advanced courses taken cannot exceed advanced_courses_available")
        represented = {course.subject_area for course in self.courses if course.subject_area != "OTHER"}
        if not represented:
            raise ValueError("add at least one course in a canonical core area")
        if not represented.issubset(self.highest_levels_available):
            raise ValueError("highest_levels_available is required for every represented core area")
        if self.advanced_courses_available == 0 and any(
            level != "STANDARD" for level in self.highest_levels_available.values()
        ):
            raise ValueError("highest levels cannot be advanced when no advanced courses are available")
        if self.advanced_courses_available > 0 and not self.advanced_program_types:
            raise ValueError("advanced_program_types are required when advanced courses are available")
        return self


class CourseworkComponent(ApiModel):
    key: CourseworkComponentKey
    label: str
    score: float | None
    points: int
    points_available: int
    evidence: str
    rule: str
    explanation: str


class CourseworkEvaluationResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "coursework-1.0.0"
    overall_score: float
    display_score: int
    rating: CourseworkRating
    confidence: CourseworkConfidence
    components: list[CourseworkComponent]
    school_context: str
    no_advanced_penalty: bool
    formula: str
    triggered_rules: list[dict[str, str]] = Field(default_factory=list)
