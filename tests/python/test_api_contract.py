import logging
import uuid

import pytest
from fastapi.testclient import TestClient

from api.admission_engine.application.factory import create_app


def test_validation_and_domain_errors_use_stable_envelope() -> None:
    with TestClient(create_app()) as client:
        invalid = client.post("/api/v1/evaluations/essay", json={"text": ""})
        assert invalid.status_code == 422
        assert invalid.json()["error"]["code"] == "INVALID_INPUT"
        compare = client.post("/api/v1/evaluations/essay/compare", json=[])
        assert compare.status_code == 400
        assert compare.json()["error"]["code"] == "INVALID_INPUT"
        assert compare.headers["cache-control"] == "no-store"


def test_public_analysis_does_not_echo_script_input() -> None:
    text = "<script>alert('x')</script> I learned from testing 14 prototypes."
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/evaluations/essay",
            json={"text": text, "min_words": 0, "word_limit": 650, "save": True},
        )
    assert response.status_code == 200
    assert text not in response.text
    assert response.headers["x-request-id"]
    assert response.headers["x-content-type-options"] == "nosniff"


def test_essay_api_exposes_complete_explainability_contract() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/evaluations/essay",
            json={
                "essay_type": "SCHOLARSHIP",
                "text": "I learned from testing twelve prototypes.",
                "min_words": 250,
                "word_limit": 650,
                "prompt_text": "Describe a meaningful project.",
                "save_raw_text": True,
            },
        )
        invalid_type = client.post(
            "/api/v1/evaluations/essay",
            json={"essay_type": "UNSUPPORTED", "text": "Draft"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["rubric_version"] == "essay-1.0.0"
    assert set(payload["data"]["evaluation"]["components"]) == {
        "compliance",
        "clarity",
        "structure",
        "specificity",
        "reflection",
        "voice",
        "sentence_variety",
        "style_hygiene",
    }
    finding = payload["data"]["evaluation"]["issues"][0]
    assert {
        "rule_id",
        "severity",
        "title",
        "message",
        "evidence",
        "score_effect",
        "confidence",
        "methodology_link",
    } <= finding.keys()
    assert invalid_type.status_code == 422


def test_essay_upload_rejects_csv_even_when_generic_parser_supports_it() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/evaluations/essay/upload",
            files={"file": ("draft.csv", b"essay,content", "text/csv")},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE"


def test_methodology_is_public_and_versioned() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/methodology")
    assert response.status_code == 200
    assert response.json()["data"]["engine_version"] == "2.0.0"


def test_internal_openapi_is_disabled_and_host_is_validated() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/openapi.json").status_code == 404
        rejected = client.get("/api/v1/health", headers={"Host": "attacker.example"})
    assert rejected.status_code == 400


def test_upload_form_limits_return_client_errors() -> None:
    files = {"file": ("draft.txt", b"small draft", "text/plain")}
    with TestClient(create_app()) as client:
        invalid_range = client.post(
            "/api/v1/evaluations/essay/upload",
            files=files,
            data={"min_words": "2", "word_limit": "1"},
        )
        oversized_type = client.post(
            "/api/v1/evaluations/essay/upload",
            files=files,
            data={"essay_type": "x" * 81},
        )
    assert invalid_range.status_code == 400
    assert invalid_range.json()["error"]["code"] == "INVALID_INPUT"
    assert oversized_type.status_code == 422


def test_protected_routes_require_authentication() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/me").status_code == 401
        assert client.get("/api/v1/profiles").status_code == 401
        assert client.get("/api/v1/admin/system").status_code == 401
        saved_compare = client.post(
            "/api/v1/evaluations/essay/compare",
            json={
                "left_evaluation_id": str(uuid.uuid4()),
                "right_evaluation_id": str(uuid.uuid4()),
            },
        )
        assert saved_compare.status_code == 401


def test_saved_compare_requires_distinct_evaluations() -> None:
    evaluation_id = str(uuid.uuid4())
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/evaluations/essay/compare",
            json={
                "left_evaluation_id": evaluation_id,
                "right_evaluation_id": evaluation_id,
            },
        )
    assert response.status_code == 422


def test_untrusted_cors_origin_is_not_reflected() -> None:
    with TestClient(create_app()) as client:
        response = client.options(
            "/api/v1/evaluations/essay",
            headers={"Origin": "https://attacker.example", "Access-Control-Request-Method": "POST"},
        )
    assert "access-control-allow-origin" not in response.headers


def test_rate_limit_returns_stable_error() -> None:
    with TestClient(create_app()) as client:
        responses = [
            client.post(
                "/api/v1/evaluations/essay", json={"text": "A measurable sentence.", "min_words": 0}
            )
            for _ in range(21)
        ]
    assert responses[-1].status_code == 429
    assert responses[-1].json()["error"]["code"] == "RATE_LIMITED"


def test_internal_errors_are_sanitized(caplog: pytest.LogCaptureFixture) -> None:
    app = create_app()

    @app.get("/explode")
    def explode() -> None:
        raise RuntimeError("database-password-must-not-leak")

    with (
        caplog.at_level(logging.ERROR, logger="evalio.api"),
        TestClient(app, raise_server_exceptions=False) as client,
    ):
        response = client.get("/explode")
    assert response.status_code == 500
    assert "database-password" not in response.text
    assert "database-password" not in caplog.text
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
