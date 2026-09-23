import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.admission_engine.application.factory import create_app
from api.admission_engine.engine.essay_ideas import build_essay_ideas
from api.admission_engine.schemas.essay_ideas import EssayIdeaBuildRequest


def request_payload() -> dict[str, object]:
    return {
        "essay_type": "COMMON_APP",
        "prompt_selection": "Common App Prompt 5",
        "specific_moments": ["The 3 AM server outage", "The failed field test", "The team meeting"],
        "values": ["responsibility"],
        "challenges": ["Being responsible while unprepared"],
        "lessons_or_changes": ["I learned to test assumptions before scaling"],
        "people_or_places": ["The community lab"],
    }


def test_builder_is_deterministic_and_uses_only_grounded_fields() -> None:
    request = EssayIdeaBuildRequest.model_validate(request_payload())
    left = build_essay_ideas(request)
    right = build_essay_ideas(request)

    assert left == right
    assert len(left.ideas) == 3
    assert left.ideas[0].moment == "The 3 AM server outage"
    assert left.ideas[0].tension == "Being responsible while unprepared"
    assert left.ideas[0].core_value == "responsibility"
    assert left.ideas[0].change == "I learned to test assumptions before scaling"
    assert left.ideas[0].possible_fit == "Common App Prompt 5"


def test_editing_input_predictably_changes_output() -> None:
    original = EssayIdeaBuildRequest.model_validate(request_payload())
    edited_payload = request_payload()
    edited_payload["values"] = ["curiosity"]
    edited = EssayIdeaBuildRequest.model_validate(edited_payload)

    original_result = build_essay_ideas(original)
    edited_result = build_essay_ideas(edited)

    assert original_result != edited_result
    assert edited_result.ideas[0].core_value == "curiosity"


def test_builder_rejects_ungrounded_or_insufficient_combinations() -> None:
    with pytest.raises(ValidationError):
        EssayIdeaBuildRequest.model_validate({})
    payload = request_payload()
    payload["specific_moments"] = ["Only one moment"]
    with pytest.raises(ValidationError, match="at least three grounded directions"):
        EssayIdeaBuildRequest.model_validate(payload)


def test_builder_caps_output_at_eight_directions() -> None:
    payload = request_payload()
    payload["values"] = ["curiosity", "responsibility", "service", "learning"]
    result = build_essay_ideas(EssayIdeaBuildRequest.model_validate(payload))
    assert len(result.ideas) == 8


def test_public_builder_api_is_versioned_and_not_cached() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/essay-ideas/build", json=request_payload())

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    payload = response.json()
    assert payload["meta"]["builder_version"] == "idea-builder-1.0.0"
    assert len(payload["data"]["result"]["ideas"]) == 3
