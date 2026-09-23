from datetime import date
from typing import Any, cast

import pytest
from pydantic import ValidationError

from api.admission_engine.config import (
    RUBRIC_VERSIONS,
    V1_RUBRIC_VERSIONS,
    V2_RUBRIC_VERSIONS,
    rubric_versions_for,
)
from api.admission_engine.config.settings import Settings
from api.admission_engine.engine.enums import ConfidenceLevel
from api.admission_engine.engine.scoring import round_display, round_internal, weighted_result
from api.admission_engine.engine.v2.models import (
    ConfidenceV2,
    NumericEvaluationV2,
    StatusEvaluationV2,
)
from api.admission_engine.engine.v2.regression import compare_regression, normalize_result
from api.admission_engine.engine.v2.rules import V2_RULE_REGISTRY


def test_v1_remains_the_default_and_existing_rubrics_are_unchanged() -> None:
    assert Settings().SCORING_ENGINE_VERSION == "v1"
    assert RUBRIC_VERSIONS == V1_RUBRIC_VERSIONS
    assert RUBRIC_VERSIONS["essay"] == "essay-1.0.0"
    assert rubric_versions_for("v1") == V1_RUBRIC_VERSIONS


def test_v2_track_is_explicit_and_rejects_unknown_values() -> None:
    assert Settings(SCORING_ENGINE_VERSION="v2").SCORING_ENGINE_VERSION == "v2"
    assert rubric_versions_for("v2") == V2_RUBRIC_VERSIONS
    assert V2_RUBRIC_VERSIONS["essay"] == "essay-craft-2.0.0"
    with pytest.raises((ValidationError, ValueError)):
        Settings(SCORING_ENGINE_VERSION=cast(Any, "future"))
    with pytest.raises(ValueError, match="Unsupported"):
        rubric_versions_for("future")


def test_v2_weighting_redistributes_only_across_available_values() -> None:
    result = weighted_result(
        {"achievement": 80, "rigor": None, "trend": 100},
        {"achievement": 0.55, "rigor": 0.35, "trend": 0.10},
    )
    assert result.score == 83.08
    assert result.effective_weights == pytest.approx(
        {"achievement": 0.55 / 0.65, "trend": 0.10 / 0.65}
    )
    assert weighted_result({"missing": None}, {"missing": 1}).score is None


@pytest.mark.parametrize(
    ("raw", "internal", "display"),
    [(84.444, 84.44, 84), (84.445, 84.45, 84), (84.5, 84.5, 85), (101, 100.0, 100)],
)
def test_v2_rounding_and_clamping(raw: float, internal: float, display: int) -> None:
    assert round_internal(raw) == internal
    assert round_display(raw) == display


@pytest.mark.parametrize(
    ("score", "band"),
    [(64.99, ConfidenceLevel.LOW), (65, ConfidenceLevel.MEDIUM), (84.99, ConfidenceLevel.MEDIUM), (85, ConfidenceLevel.HIGH)],
)
def test_v2_confidence_boundaries(score: float, band: ConfidenceLevel) -> None:
    assert ConfidenceV2.from_score(score).band == band


def test_v2_numeric_and_status_only_shapes_are_distinct() -> None:
    numeric = NumericEvaluationV2(
        rubric_version="academic-2.0.0",
        overall_score=88.42,
        display_score=88,
        confidence=ConfidenceV2.from_score(91),
        evaluation_date=date(2026, 9, 20),
    )
    status = StatusEvaluationV2(
        rubric_version="financial-fit-2.0.0",
        status="POTENTIALLY_AFFORDABLE",
        confidence=ConfidenceV2.from_score(76),
        evaluation_date=date(2026, 9, 20),
    )
    assert numeric.overall_score == 88.42
    assert "overall_score" not in status.model_dump()
    with pytest.raises(ValidationError, match="canonical rounding"):
        NumericEvaluationV2(
            rubric_version="academic-2.0.0",
            overall_score=88.421,
            display_score=88,
            confidence=ConfidenceV2.from_score(91),
            evaluation_date=date(2026, 9, 20),
        )


def test_every_rulebook_v2_id_is_registered_once() -> None:
    assert len(V2_RULE_REGISTRY) == 98
    assert len(V2_RULE_REGISTRY) == len(set(V2_RULE_REGISTRY))
    assert V2_RULE_REGISTRY["ACAD2-001"].rubric_version == "academic-2.0.0"
    assert V2_RULE_REGISTRY["CONF2-005"].rubric_version == "confidence-2.0.0"


def test_regression_comparison_distinguishes_expected_changes() -> None:
    expected = compare_regression(
        fixture_id="A2",
        domain="academic",
        v1_score_or_status=72,
        v2_score_or_status=88,
        expected_reason="No penalty for unavailable advanced courses.",
    )
    unexpected = compare_regression(
        fixture_id="A1",
        domain="academic",
        v1_score_or_status=90,
        v2_score_or_status=89,
    )
    assert expected.delta_or_change == 16
    assert expected.unexpected_change is False
    assert unexpected.unexpected_change is True


def test_regression_normalization_is_deterministic_and_removes_telemetry() -> None:
    left = normalize_result({"z": 1, "request_id": "left", "nested": {"evaluated_at": "now", "a": 2}})
    right = normalize_result({"nested": {"a": 2, "evaluated_at": "later"}, "request_id": "right", "z": 1})
    assert left == right == {"nested": {"a": 2}, "z": 1}
