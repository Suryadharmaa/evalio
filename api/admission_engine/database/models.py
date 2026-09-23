import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.admission_engine.database.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_subject: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email_snapshot: Mapped[str | None] = mapped_column(String(320))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    profiles: Mapped[list["ApplicantProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class EssayReviewCache(TimestampMixin, Base):
    __tablename__ = "essay_review_cache"
    __table_args__ = (
        UniqueConstraint("essay_hash", "rubric_version", "analysis_version", "model_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    essay_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    rubric_version: Mapped[str] = mapped_column(String(40), nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(40), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    result_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    local_metrics: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class ApplicantProfile(TimestampMixin, Base):
    __tablename__ = "applicant_profiles"
    __table_args__ = (Index("ix_applicant_profiles_user_id_id", "user_id", "id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    profile_name: Mapped[str] = mapped_column(String(120), nullable=False)
    applicant_type: Mapped[str] = mapped_column(String(24), nullable=False, default="UNKNOWN")
    country_code: Mapped[str | None] = mapped_column(String(2))
    graduation_year: Mapped[int | None] = mapped_column(Integer)
    curriculum_type: Mapped[str | None] = mapped_column(String(80))
    grading_scale_name: Mapped[str | None] = mapped_column(String(80))
    grading_scale_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    grading_scale_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    intended_major: Mapped[str | None] = mapped_column(String(160))
    school_name: Mapped[str | None] = mapped_column(String(240))
    class_size: Mapped[int | None] = mapped_column(Integer)
    class_rank: Mapped[int | None] = mapped_column(Integer)
    max_family_contribution: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    budget_currency: Mapped[str | None] = mapped_column(String(3))
    requires_need_based_aid: Mapped[bool | None] = mapped_column(Boolean)

    user: Mapped[User] = relationship(back_populates="profiles")


class College(TimestampMixin, Base):
    __tablename__ = "colleges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(240))
    normalized_name: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    ipeds_id: Mapped[str | None] = mapped_column(String(20), unique=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="US")
    state_region: Mapped[str | None] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(120))
    institution_type: Mapped[str | None] = mapped_column(String(80))
    selection_group: Mapped[str | None] = mapped_column(String(80))
    application_platform_primary: Mapped[str | None] = mapped_column(String(40))
    application_platforms: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    official_website: Mapped[str | None] = mapped_column(String(500))
    common_app_member: Mapped[bool | None] = mapped_column(Boolean)
    identity_confidence: Mapped[str | None] = mapped_column(String(24))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CollegeAdmissions(TimestampMixin, Base):
    __tablename__ = "college_admissions"
    __table_args__ = (UniqueConstraint("college_id", "academic_cycle"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    academic_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    source_cycle: Mapped[str | None] = mapped_column(String(80))
    applicants_total: Mapped[int | None] = mapped_column(Integer)
    admits_total: Mapped[int | None] = mapped_column(Integer)
    enrolled_total: Mapped[int | None] = mapped_column(Integer)
    acceptance_rate: Mapped[Decimal | None] = mapped_column(Numeric(7, 6))
    yield_rate_pct: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    international_applicants: Mapped[int | None] = mapped_column(Integer)
    international_admits: Mapped[int | None] = mapped_column(Integer)
    sat_25: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    sat_50: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    sat_75: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    act_25: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    act_50: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    act_75: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    test_policy: Mapped[str] = mapped_column(String(48), nullable=False, default="UNKNOWN")
    test_policy_status: Mapped[str | None] = mapped_column(String(80))
    application_fee_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    application_fee_status: Mapped[str | None] = mapped_column(String(80))


class CollegeRequirement(Base):
    __tablename__ = "college_requirements"
    __table_args__ = (UniqueConstraint("college_id", "academic_cycle", "requirement_type"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    academic_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    word_limit: Mapped[int | None] = mapped_column(Integer)
    quantity: Mapped[int | None] = mapped_column(Integer)


class CollegeFinancialAid(TimestampMixin, Base):
    __tablename__ = "college_financial_aid"
    __table_args__ = (UniqueConstraint("college_id", "academic_cycle"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    academic_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    source_cycle: Mapped[str | None] = mapped_column(String(80))
    need_policy: Mapped[str] = mapped_column(String(48), nullable=False, default="UNKNOWN")
    aid_policy_status: Mapped[str | None] = mapped_column(String(80))
    international_need_based_aid: Mapped[bool | None] = mapped_column(Boolean)
    international_need_based_aid_status: Mapped[str | None] = mapped_column(String(40))
    meets_full_demonstrated_need: Mapped[bool | None] = mapped_column(Boolean)
    meets_full_demonstrated_need_status: Mapped[str | None] = mapped_column(String(64))
    css_profile_required: Mapped[bool | None] = mapped_column(Boolean)
    estimated_cost_of_attendance: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    tuition: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    mandatory_fees: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    room_board: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    books_personal: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cost_basis: Mapped[str | None] = mapped_column(String(80))
    aid_forms_or_process: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notes: Mapped[str | None] = mapped_column(Text)


class CollegeCdsFactor(Base):
    __tablename__ = "college_cds_factors"
    __table_args__ = (UniqueConstraint("college_id", "academic_cycle", "factor_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    academic_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    factor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    importance: Mapped[str] = mapped_column(String(24), nullable=False)


class CollegeSource(Base):
    __tablename__ = "college_sources"
    __table_args__ = (
        UniqueConstraint(
            "college_id", "field_group", "field_name", "source_url", "academic_cycle"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    field_group: Mapped[str] = mapped_column(String(80), nullable=False)
    field_name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1_000), nullable=False)
    academic_cycle: Mapped[str | None] = mapped_column(String(20))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    freshness: Mapped[str] = mapped_column(String(24), nullable=False)
    confidence: Mapped[str] = mapped_column(String(24), nullable=False)
    value_hash: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)


class CollegeMedia(Base):
    __tablename__ = "college_media"
    __table_args__ = (
        UniqueConstraint("college_id", "image_url"),
        Index(
            "uq_college_media_primary_type",
            "college_id",
            "media_type",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(24), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1_000), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1_000), nullable=False)
    license: Mapped[str] = mapped_column(String(80), nullable=False)
    attribution: Mapped[str | None] = mapped_column(String(500))
    alt_text: Mapped[str] = mapped_column(String(300), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    sha256: Mapped[str | None] = mapped_column(String(64))
    content_type: Mapped[str | None] = mapped_column(String(100))
    verification_quality: Mapped[str | None] = mapped_column(String(40))
    trademark_notice: Mapped[bool | None] = mapped_column(Boolean)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AdminImportRun(Base):
    __tablename__ = "admin_import_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    import_type: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), unique=True)
    academic_cycle: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    rows_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_valid: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    diff_summary: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AcademicTerm(TimestampMixin, Base):
    __tablename__ = "academic_terms"
    __table_args__ = (UniqueConstraint("profile_id", "term_order"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    term_order: Mapped[int] = mapped_column(Integer, nullable=False)
    term_name: Mapped[str] = mapped_column(String(80), nullable=False)
    school_year: Mapped[str] = mapped_column(String(20), nullable=False)
    average_grade: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    scale_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    scale_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    term_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_terms.id", ondelete="SET NULL")
    )
    course_name: Mapped[str] = mapped_column(String(160), nullable=False)
    subject_area: Mapped[str | None] = mapped_column(String(80))
    course_level: Mapped[str | None] = mapped_column(String(80))
    grade_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    grade_text: Mapped[str | None] = mapped_column(String(40))
    is_advanced: Mapped[bool | None] = mapped_column(Boolean)
    is_highest_available: Mapped[bool | None] = mapped_column(Boolean)
    is_major_related: Mapped[bool | None] = mapped_column(Boolean)


class SchoolContext(Base):
    __tablename__ = "school_context"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applicant_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    advanced_courses_available: Mapped[int | None] = mapped_column(Integer)
    advanced_program_types: Mapped[list[str] | None] = mapped_column(JSONB)
    highest_course_levels: Mapped[dict[str, str] | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)


class TestScore(Base):
    __tablename__ = "test_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    test_type: Mapped[str] = mapped_column(String(40), nullable=False)
    composite_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    section_scores: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    test_date: Mapped[date | None] = mapped_column(Date)
    is_official: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Activity(TimestampMixin, Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    activity_order: Mapped[int | None] = mapped_column(Integer)
    activity_name: Mapped[str] = mapped_column(String(160), nullable=False)
    position_title: Mapped[str | None] = mapped_column(String(160))
    organization_name: Mapped[str | None] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(80))
    hours_per_week: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    weeks_per_year: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    duration_months: Mapped[int | None] = mapped_column(Integer)
    participant_count: Mapped[int | None] = mapped_column(Integer)
    people_impacted: Mapped[int | None] = mapped_column(Integer)
    leadership_level: Mapped[str | None] = mapped_column(String(40))
    recognition_scope: Mapped[str | None] = mapped_column(String(40))
    progression_level: Mapped[int | None] = mapped_column(Integer)
    is_founder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Honor(Base):
    __tablename__ = "honors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    honor_name: Mapped[str] = mapped_column(String(240), nullable=False)
    scope: Mapped[str | None] = mapped_column(String(40))
    placement: Mapped[str | None] = mapped_column(String(80))
    participant_count: Mapped[int | None] = mapped_column(Integer)
    selection_rate: Mapped[Decimal | None] = mapped_column(Numeric(7, 6))
    organizer: Mapped[str | None] = mapped_column(String(240))
    countries_represented: Mapped[int | None] = mapped_column(Integer)
    academic_area: Mapped[str | None] = mapped_column(String(120))
    grade_received: Mapped[str | None] = mapped_column(String(40))
    repeat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Essay(TimestampMixin, Base):
    __tablename__ = "essays"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    essay_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str | None] = mapped_column(String(240))
    prompt_text: Mapped[str | None] = mapped_column(Text)
    word_limit: Mapped[int | None] = mapped_column(Integer)
    min_words: Mapped[int | None] = mapped_column(Integer)
    raw_text: Mapped[str | None] = mapped_column(Text)
    save_raw_text: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class EssayMetric(Base):
    __tablename__ = "essay_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    essay_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("essays.id", ondelete="CASCADE"), nullable=False
    )
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False)
    sentence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    paragraph_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_sentence_length: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    median_sentence_length: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    sentence_length_stddev: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    avg_paragraph_length: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    flesch_reading_ease: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    flesch_kincaid_grade: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    lexical_diversity: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    reflection_density: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    specificity_density: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    repetition_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    metrics_version: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recommender_role: Mapped[str | None] = mapped_column(String(80))
    relationship_duration_months: Mapped[int | None] = mapped_column(Integer)
    raw_text: Mapped[str | None] = mapped_column(Text)
    save_raw_text: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TargetCollege(TimestampMixin, Base):
    __tablename__ = "target_colleges"
    __table_args__ = (UniqueConstraint("profile_id", "college_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    priority: Mapped[int | None] = mapped_column(Integer)
    application_round: Mapped[str | None] = mapped_column(String(40))
    application_status: Mapped[str | None] = mapped_column(String(40))


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE")
    )
    evaluation_type: Mapped[str] = mapped_column(String(40), nullable=False)
    subject_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    college_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="SET NULL")
    )
    engine_version: Mapped[str] = mapped_column(String(40), nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(40), nullable=False)
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    display_score: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evaluation_date: Mapped[date] = mapped_column(Date, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvaluationComponent(Base):
    __tablename__ = "evaluation_components"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    component_name: Mapped[str] = mapped_column(String(80), nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    weight: Mapped[Decimal | None] = mapped_column(Numeric(7, 6))
    weighted_value: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    status: Mapped[str] = mapped_column(String(24), nullable=False)


class TriggeredRule(Base):
    __tablename__ = "triggered_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(40), nullable=False)
    severity: Mapped[str] = mapped_column(String(24), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    score_delta: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    confidence: Mapped[str] = mapped_column(String(24), nullable=False)
    evidence: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ApplicationMaterialStatus(Base):
    __tablename__ = "application_material_status"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    requirement_type: Mapped[str] = mapped_column(String(80), nullable=False)
    completion_status: Mapped[str] = mapped_column(String(40), nullable=False)
    linked_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SavedReport(Base):
    __tablename__ = "saved_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    report_version: Mapped[str] = mapped_column(String(40), nullable=False)
    report_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RateLimitBucket(Base):
    __tablename__ = "rate_limit_buckets"
    __table_args__ = (
        UniqueConstraint("subject_hash", "route_key", "window_start"),
        Index("ix_rate_limit_buckets_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    route_key: Mapped[str] = mapped_column(String(160), nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
