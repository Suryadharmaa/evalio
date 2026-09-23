import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field, model_validator

from api.admission_engine.engine.enums import ApplicantType
from api.admission_engine.schemas.common import ApiModel


class ProfileFields(ApiModel):
    profile_name: str = Field(min_length=1, max_length=120)
    applicant_type: ApplicantType = ApplicantType.UNKNOWN
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    graduation_year: int | None = Field(default=None, ge=2020, le=2100)
    curriculum_type: str | None = Field(default=None, max_length=80)
    grading_scale_name: str | None = Field(default=None, max_length=80)
    grading_scale_min: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    grading_scale_max: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    intended_major: str | None = Field(default=None, max_length=160)
    school_name: str | None = Field(default=None, max_length=240)
    class_size: int | None = Field(default=None, ge=1, le=100_000)
    class_rank: int | None = Field(default=None, ge=1, le=100_000)
    max_family_contribution: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=2
    )
    budget_currency: str | None = Field(default=None, min_length=3, max_length=3)
    requires_need_based_aid: bool | None = None

    @model_validator(mode="after")
    def validate_scale_and_rank(self) -> "ProfileFields":
        if (
            self.grading_scale_min is not None
            and self.grading_scale_max is not None
            and self.grading_scale_min >= self.grading_scale_max
        ):
            raise ValueError("grading_scale_max must be greater than grading_scale_min")
        if (
            self.class_rank is not None
            and self.class_size is not None
            and self.class_rank > self.class_size
        ):
            raise ValueError("class_rank cannot exceed class_size")
        return self


class ProfileCreate(ProfileFields):
    pass


class ProfileUpdate(ApiModel):
    profile_name: str | None = Field(default=None, min_length=1, max_length=120)
    applicant_type: ApplicantType | None = None
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    graduation_year: int | None = Field(default=None, ge=2020, le=2100)
    curriculum_type: str | None = Field(default=None, max_length=80)
    grading_scale_name: str | None = Field(default=None, max_length=80)
    grading_scale_min: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    grading_scale_max: Decimal | None = Field(default=None, max_digits=10, decimal_places=3)
    intended_major: str | None = Field(default=None, max_length=160)
    school_name: str | None = Field(default=None, max_length=240)
    class_size: int | None = Field(default=None, ge=1, le=100_000)
    class_rank: int | None = Field(default=None, ge=1, le=100_000)
    max_family_contribution: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=2
    )
    budget_currency: str | None = Field(default=None, min_length=3, max_length=3)
    requires_need_based_aid: bool | None = None


class ProfileRead(ProfileFields):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
