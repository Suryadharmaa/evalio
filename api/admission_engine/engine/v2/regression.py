from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import Field

from api.admission_engine.engine.models import StrictModel

_VOLATILE_KEYS = frozenset({"request_id", "evaluated_at", "runtime_ms", "runtime_timing"})


def normalize_result(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {key: normalize_result(item) for key, item in sorted(value.items()) if key not in _VOLATILE_KEYS}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [normalize_result(item) for item in value]
    return value


class RegressionComparison(StrictModel):
    fixture_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    v1_score_or_status: float | str | None
    v2_score_or_status: float | str | None
    delta_or_change: float | str | None
    expected_reason: str | None = None
    unexpected_change: bool


def compare_regression(
    *,
    fixture_id: str,
    domain: str,
    v1_score_or_status: float | str | None,
    v2_score_or_status: float | str | None,
    expected_reason: str | None = None,
) -> RegressionComparison:
    changed = v1_score_or_status != v2_score_or_status
    if isinstance(v1_score_or_status, (int, float)) and isinstance(v2_score_or_status, (int, float)):
        delta: float | str | None = round(v2_score_or_status - v1_score_or_status, 2)
    elif changed:
        delta = f"{v1_score_or_status} -> {v2_score_or_status}"
    else:
        delta = None
    return RegressionComparison(
        fixture_id=fixture_id,
        domain=domain,
        v1_score_or_status=v1_score_or_status,
        v2_score_or_status=v2_score_or_status,
        delta_or_change=delta,
        expected_reason=expected_reason,
        unexpected_change=changed and not expected_reason,
    )
