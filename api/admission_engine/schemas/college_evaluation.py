from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import Field

from api.admission_engine.engine.enums import (
    CompletionStatus,
    DataFreshness,
    NeedPolicy,
    RequirementStatus,
    TestPolicy,
)
from api.admission_engine.schemas.common import ApiModel


class PublishedRange(ApiModel):
    lower: float
    median: float
    upper: float


ApplicationComponent = Literal[
    "academics", "testing", "activities", "honors", "essay", "recommendations"
]
CdsImportance = Literal["VERY_IMPORTANT", "IMPORTANT", "CONSIDERED", "NOT_CONSIDERED", "UNKNOWN"]
ComponentScore = Annotated[float, Field(ge=0, le=100)]


class CollegeEvaluationRequest(ApiModel):
    academic_strength: float | None = Field(default=None, ge=0, le=100)
    applicant_test_score: float | None = None
    published_test_range: PublishedRange | None = None
    test_policy: TestPolicy = TestPolicy.UNKNOWN
    acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    requirements_known: bool = True
    required_materials_complete: bool = True
    profile_completeness: int = Field(default=0, ge=0, le=35)
    source_freshness_points: int = Field(default=0, ge=0, le=25)
    college_data_completeness: int = Field(default=0, ge=0, le=20)
    metric_reliability: int = Field(default=0, ge=0, le=20)
    critical_source_stale: bool = False
    multiple_critical_unknown: bool = False
    application_components: dict[ApplicationComponent, ComponentScore] = Field(
        default_factory=dict, max_length=6
    )
    cds_importance: dict[ApplicationComponent, CdsImportance] = Field(
        default_factory=dict, max_length=6
    )
    unmapped_cds_factors: int = Field(default=0, ge=0, le=100)


class CollegeEvaluationResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "college-1.1.0"
    academic_alignment: float | None
    application_strength: float | None
    components: dict[ApplicationComponent, ComponentScore] = Field(default_factory=dict)
    requirements_fit: Literal["COMPATIBLE", "INCOMPLETE", "UNKNOWN"]
    selectivity_risk: Literal[
        "EXTREME", "VERY_HIGH", "HIGH", "MODERATE_HIGH", "MODERATE", "LOWER", "UNKNOWN"
    ]
    planning_category: Literal[
        "HIGH_REACH", "REACH", "COMPETITIVE", "LIKELY_ISH", "INSUFFICIENT_DATA"
    ]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    confidence_score: int
    reasons: list[str]
    triggered_rules: list[str] = Field(default_factory=list)


class FinancialEvaluationRequest(ApiModel):
    applicant_type: Literal["DOMESTIC", "INTERNATIONAL", "UNKNOWN"]
    requires_substantial_aid: bool
    max_family_contribution: float | None = Field(default=None, ge=0)
    estimated_required_contribution: float | None = Field(default=None, ge=0)
    need_policy: NeedPolicy = NeedPolicy.UNKNOWN
    international_need_based_aid: bool | None = None
    cost_freshness: DataFreshness = DataFreshness.UNKNOWN


class FinancialEvaluationResponse(ApiModel):
    fit: Literal["STRONG", "POSSIBLE", "POOR", "INCOMPATIBLE", "UNKNOWN"]
    risk: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    reasons: list[str]
    triggered_rules: list[str]


class MaterialStatus(ApiModel):
    requirement_type: str = Field(min_length=1, max_length=80)
    requirement_status: RequirementStatus
    completion_status: CompletionStatus
    deadline: datetime | None = None
    quality_evaluated: bool = False


class ApplicationAuditRequest(ApiModel):
    evaluation_date: date
    materials: list[MaterialStatus] = Field(max_length=100)


class ApplicationAuditResponse(ApiModel):
    engine_version: str = "2.0.0"
    rubric_version: str = "application-1.1.0"
    completeness_score: float
    readiness: Literal["COMPLETE", "INCOMPLETE", "DEADLINE_PASSED"]
    missing_required: list[str]
    critical_issues: list[str]
    priorities: list[str]
    checklist: list[dict[str, object]]
