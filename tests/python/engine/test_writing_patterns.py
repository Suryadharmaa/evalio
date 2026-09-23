from fastapi.testclient import TestClient

from api.admission_engine.application.factory import create_app
from api.admission_engine.engine.writing_patterns import evaluate_writing_patterns
from api.admission_engine.schemas.writing_patterns import WritingPatternRequest


def test_writing_pattern_result_is_deterministic_and_complete() -> None:
    text = " ".join(["I learned through measured practice."] * 24)
    request = WritingPatternRequest(text=text)

    left = evaluate_writing_patterns(request)
    right = evaluate_writing_patterns(request)

    assert left == right
    assert left.total_signals == 25
    assert len(left.signals) == 25
    assert len({signal.signal_id for signal in left.signals}) == 25
    assert all(signal.threshold and signal.explanation for signal in left.signals)
    repeated = next(signal for signal in left.signals if signal.signal_id == "WP-004")
    assert repeated.triggered
    assert repeated.evidence


def test_short_text_marks_sample_dependent_signals_unavailable() -> None:
    result = evaluate_writing_patterns(WritingPatternRequest(text="A short draft."))

    assert result.confidence == "LOW"
    uniformity = next(signal for signal in result.signals if signal.signal_id == "WP-001")
    assert uniformity.level == "INSUFFICIENT_DATA"
    assert not uniformity.triggered


def test_writing_pattern_api_has_versioned_non_probabilistic_contract() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/evaluations/writing-patterns",
            json={"text": " ".join(["I learned through measured practice."] * 24)},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"]
    assert payload["meta"]["rubric_version"] == "writing-patterns-1.0.0"
    evaluation = payload["data"]["evaluation"]
    assert evaluation["risk"] in {"LOW", "MODERATE", "HIGH"}
    assert "probability" not in str(evaluation).casefold()
    assert "authorship" not in evaluation


def test_writing_pattern_api_rejects_empty_and_extra_fields() -> None:
    with TestClient(create_app()) as client:
        empty = client.post("/api/v1/evaluations/writing-patterns", json={"text": ""})
        extra = client.post(
            "/api/v1/evaluations/writing-patterns",
            json={"text": "Draft", "ai_probability": True},
        )

    assert empty.status_code == 422
    assert extra.status_code == 422
