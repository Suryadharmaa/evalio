import json
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from api.admission_engine.schemas.common import ApiModel


class ReportRequest(ApiModel):
    report_type: str = Field(min_length=1, max_length=80)
    profile_id: str | None = None
    sections: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_payload_size(self) -> "ReportRequest":
        if len(json.dumps(self.sections, default=str).encode()) > 500_000:
            raise ValueError("report sections exceed 500 KB")
        return self


class StructuredReport(ApiModel):
    report_version: str = "1.0.0"
    engine_version: str = "2.0.0"
    report_type: str
    profile_id: str | None
    sections: dict[str, Any]
    generated_at: datetime
    disclaimer: str = "Evalio metrics are internal planning tools, not official ratings or admission probabilities."


class SavedReportProfileSection(ApiModel):
    profile_name: str = Field(min_length=1, max_length=120)


class SavedReportEvaluationSection(ApiModel):
    evaluation_type: str = Field(min_length=1, max_length=40)
    display_score: int | None = Field(default=None, ge=0, le=100)
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    evaluated_at: datetime


class SavedReportSections(ApiModel):
    profile: SavedReportProfileSection
    latest_evaluations: list[SavedReportEvaluationSection] = Field(max_length=20)


class SavedReportCreate(ApiModel):
    report_type: Literal["APPLICATION_READINESS"]
    sections: SavedReportSections

    @model_validator(mode="after")
    def validate_payload_size(self) -> "SavedReportCreate":
        if len(json.dumps(self.sections.model_dump(mode="json"), default=str).encode()) > 500_000:
            raise ValueError("report sections exceed 500 KB")
        return self


class SavedReportRead(ApiModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    report_type: str
    report_version: str
    report_json: dict[str, Any]
    created_at: datetime
