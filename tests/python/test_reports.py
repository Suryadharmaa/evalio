import pytest
from pydantic import ValidationError

from api.admission_engine.routers.reports import _contains_raw_text
from api.admission_engine.schemas.reports import SavedReportCreate


def test_report_raw_text_guard_is_recursive() -> None:
    assert _contains_raw_text({"essay": {"raw_text": "private"}})
    assert _contains_raw_text({"items": [{"recommendation_text": "private"}]})
    assert not _contains_raw_text({"essay": {"score": 82, "issues": ["ESSAY-001"]}})


def test_saved_report_payload_has_bounded_size() -> None:
    with pytest.raises(ValidationError):
        SavedReportCreate.model_validate(
            {"report_type": "READINESS", "sections": {"oversized": "x" * 500_001}}
        )


def test_saved_report_rejects_unstructured_or_raw_content() -> None:
    with pytest.raises(ValidationError):
        SavedReportCreate.model_validate(
            {
                "report_type": "APPLICATION_READINESS",
                "sections": {
                    "profile": {"profile_name": "2027", "raw_text": "private"},
                    "latest_evaluations": [],
                },
            }
        )
