import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from api.admission_engine.engine.enums import NeedPolicy, TestPolicy
from api.admission_engine.schemas.common import ApiModel


class MediaRead(ApiModel):
    id: uuid.UUID
    media_type: str
    image_url: str
    source_url: str
    license: str
    attribution: str | None
    alt_text: str
    is_primary: bool
    width: int | None
    height: int | None
    sha256: str | None
    content_type: str | None
    verification_quality: str | None
    trademark_notice: bool | None
    verified_at: datetime


class CollegeSummary(ApiModel):
    id: uuid.UUID
    slug: str
    name: str
    official_name: str | None
    country_code: str
    state_region: str | None
    city: str | None
    institution_type: str | None
    selection_group: str | None
    identity_confidence: str | None
    application_platform_primary: str | None
    application_platforms: list[str]
    official_website: str | None
    test_policy: str | None = None
    need_policy: str | None = None
    primary_media: MediaRead | None = None


class AdmissionSnapshot(ApiModel):
    academic_cycle: str
    source_cycle: str | None
    applicants_total: int | None
    admits_total: int | None
    enrolled_total: int | None
    acceptance_rate: Decimal | None
    yield_rate_pct: Decimal | None
    international_applicants: int | None
    international_admits: int | None
    sat_25: Decimal | None
    sat_50: Decimal | None
    sat_75: Decimal | None
    act_25: Decimal | None
    act_50: Decimal | None
    act_75: Decimal | None
    test_policy: str
    test_policy_status: str | None
    application_fee_usd: Decimal | None
    application_fee_status: str | None


class RequirementRead(ApiModel):
    academic_cycle: str
    requirement_type: str
    status: str
    details: str | None
    deadline: datetime | None
    word_limit: int | None
    quantity: int | None


class SourceRead(ApiModel):
    field_group: str
    field_name: str
    source_type: str
    source_url: str
    academic_cycle: str | None
    retrieved_at: datetime
    verified_at: datetime | None
    freshness: str
    confidence: str
    notes: str | None


class FinancialAidRead(ApiModel):
    academic_cycle: str
    source_cycle: str | None
    need_policy: str
    aid_policy_status: str | None
    international_need_based_aid: bool | None
    international_need_based_aid_status: str | None
    meets_full_demonstrated_need: bool | None
    meets_full_demonstrated_need_status: str | None
    css_profile_required: bool | None
    estimated_cost_of_attendance: Decimal | None
    tuition: Decimal | None
    mandatory_fees: Decimal | None
    room_board: Decimal | None
    books_personal: Decimal | None
    cost_basis: str | None
    aid_forms_or_process: str | None
    currency: str
    notes: str | None


class CdsFactorRead(ApiModel):
    academic_cycle: str
    factor_name: str
    importance: str


class CollegeDetail(CollegeSummary):
    common_app_member: bool | None
    admissions: AdmissionSnapshot | None
    requirements: list[RequirementRead]
    financial_aid: FinancialAidRead | None
    cds_factors: list[CdsFactorRead]
    sources: list[SourceRead]
    media: list[MediaRead]


class CollegeListParams(ApiModel):
    q: str | None = Field(default=None, max_length=120)
    country: str = Field(default="US", pattern=r"^[A-Za-z]{2}$")
    state: str | None = Field(default=None, max_length=80)
    test_policy: TestPolicy | None = None
    need_policy: NeedPolicy | None = None
    application_platform: str | None = Field(
        default=None, max_length=40, pattern=r"^[A-Z][A-Z0-9_]*$"
    )
    institution_type: str | None = Field(default=None, max_length=80, pattern=r"^[A-Z][A-Z0-9_]*$")
    selectivity_band: str | None = Field(default=None, pattern=r"^(UNDER_10|10_TO_20|20_TO_40|OVER_40|UNKNOWN)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)
