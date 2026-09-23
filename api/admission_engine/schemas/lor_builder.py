from typing import Literal

from pydantic import Field, ValidationInfo, field_validator

from api.admission_engine.schemas.common import ApiModel

EndorsementStrength = Literal["MEASURED", "CLEAR", "STRONG", "WITHOUT_RESERVATION"]
FrameworkItemType = Literal["USER_EVIDENCE", "SENTENCE_SHELL", "WRITING_PROMPT"]


class LorBuildRequest(ApiModel):
    recommender_role: str = Field(min_length=1, max_length=160)
    student_name: str = Field(min_length=1, max_length=160)
    relationship_context: str = Field(min_length=1, max_length=500)
    relationship_duration: str = Field(min_length=1, max_length=120)
    subject_or_context: str | None = Field(default=None, max_length=300)
    qualities: list[str] = Field(min_length=1, max_length=8)
    specific_examples: list[str] = Field(min_length=1, max_length=8)
    comparative_evidence: str | None = Field(default=None, max_length=1_000)
    community_evidence: str | None = Field(default=None, max_length=1_000)
    academic_evidence: str | None = Field(default=None, max_length=1_000)
    endorsement_strength: EndorsementStrength = "STRONG"

    @field_validator(
        "recommender_role",
        "student_name",
        "relationship_context",
        "relationship_duration",
        "subject_or_context",
        "comparative_evidence",
        "community_evidence",
        "academic_evidence",
    )
    @classmethod
    def normalize_text(cls, value: str | None, info: ValidationInfo) -> str | None:
        if value is None:
            return None
        clean = " ".join(value.split())
        if clean:
            return clean
        if info.field_name in {
            "recommender_role",
            "student_name",
            "relationship_context",
            "relationship_duration",
        }:
            raise ValueError(f"{info.field_name} cannot be blank")
        return None

    @field_validator("qualities", "specific_examples")
    @classmethod
    def normalize_items(cls, items: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in items:
            clean = " ".join(item.split())
            if not clean:
                continue
            if len(clean) > 1_000:
                raise ValueError("builder list items may contain at most 1000 characters")
            key = clean.casefold()
            if key not in seen:
                normalized.append(clean)
                seen.add(key)
        if not normalized:
            raise ValueError("add at least one non-empty item")
        return normalized


class LorFrameworkItem(ApiModel):
    item_type: FrameworkItemType
    text: str
    source_fields: list[str]


class LorFrameworkSection(ApiModel):
    key: Literal["opening", "body_1", "body_2", "body_3", "closing"]
    title: str
    purpose: str
    items: list[LorFrameworkItem]


class LorBuildResponse(ApiModel):
    engine_version: str = "2.0.0"
    builder_version: str = "lor-builder-1.0.0"
    sections: list[LorFrameworkSection]
    missing_evidence: list[str]
    ethics_notice: Literal[
        "Final wording should be reviewed and owned by the recommender."
    ] = "Final wording should be reviewed and owned by the recommender."
