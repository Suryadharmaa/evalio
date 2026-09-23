import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.admission_engine.application.factory import create_app
from api.admission_engine.engine.lor_builder import build_lor_framework
from api.admission_engine.schemas.lor_builder import LorBuildRequest


def payload() -> dict[str, object]:
    return {
        "recommender_role": "Mathematics teacher",
        "student_name": "Jordan Lee",
        "relationship_context": "Advanced calculus class and math club",
        "relationship_duration": "Two academic years",
        "subject_or_context": "Advanced calculus",
        "qualities": ["Analytical curiosity", "Collaborative leadership"],
        "specific_examples": [
            "During the modeling project, Jordan tested three approaches.",
            "Jordan organized weekly peer-review sessions for six classmates.",
        ],
        "academic_evidence": "Jordan explained an alternate proof to the class.",
        "community_evidence": "The peer-review sessions continued through the semester.",
        "comparative_evidence": "Among the strongest problem-solvers I taught this year.",
        "endorsement_strength": "STRONG",
    }


def test_builder_is_deterministic_and_every_claim_has_an_origin() -> None:
    request = LorBuildRequest.model_validate(payload())
    left = build_lor_framework(request)
    right = build_lor_framework(request)

    assert left == right
    assert [section.key for section in left.sections] == [
        "opening", "body_1", "body_2", "body_3", "closing"
    ]
    for section in left.sections:
        for item in section.items:
            if item.item_type != "WRITING_PROMPT":
                assert item.source_fields
    rendered = " ".join(item.text for section in left.sections for item in section.items)
    assert "Jordan explained an alternate proof" in rendered
    assert "won an award" not in rendered.casefold()


def test_missing_optional_evidence_becomes_placeholder_not_claim() -> None:
    data = payload()
    data.update(academic_evidence=None, community_evidence=None, comparative_evidence=None)
    result = build_lor_framework(LorBuildRequest.model_validate(data))

    assert {"academic_evidence", "community_evidence", "comparative_evidence"} <= set(
        result.missing_evidence
    )
    assert any(
        item.item_type == "WRITING_PROMPT" and item.text.startswith("[")
        for section in result.sections
        for item in section.items
    )


def test_builder_rejects_blank_required_fields_and_empty_evidence() -> None:
    data = payload()
    data["student_name"] = "   "
    with pytest.raises(ValidationError, match="student_name cannot be blank"):
        LorBuildRequest.model_validate(data)
    data = payload()
    data["specific_examples"] = ["   "]
    with pytest.raises(ValidationError, match="non-empty item"):
        LorBuildRequest.model_validate(data)


def test_editing_evidence_changes_only_grounded_output() -> None:
    original = LorBuildRequest.model_validate(payload())
    edited_data = payload()
    edited_data["qualities"] = ["Patient instruction"]
    edited = LorBuildRequest.model_validate(edited_data)

    assert build_lor_framework(original) != build_lor_framework(edited)
    assert "Patient instruction" in " ".join(
        item.text for section in build_lor_framework(edited).sections for item in section.items
    )


def test_public_lor_builder_api_is_versioned_and_not_cached() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/lor/build", json=payload())

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["meta"]["builder_version"] == "lor-builder-1.0.0"
    assert len(body["data"]["result"]["sections"]) == 5
