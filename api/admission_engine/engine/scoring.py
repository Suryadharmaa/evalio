from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def weighted_score(
    values: Mapping[str, float | None], weights: Mapping[str, float]
) -> float | None:
    included = [
        (values[name], weight) for name, weight in weights.items() if values.get(name) is not None
    ]
    if not included:
        return None
    denominator = sum(weight for _, weight in included)
    if denominator <= 0:
        return None
    return round(
        sum(float(value) * weight for value, weight in included if value is not None) / denominator,
        2,
    )


def round_internal(value: float, decimal_places: int = 2) -> float:
    """V2 score rounding; kept separate so V1's historical rounding is unchanged."""
    quantum = Decimal(1).scaleb(-decimal_places)
    return float(Decimal(str(clamp(value))).quantize(quantum, rounding=ROUND_HALF_UP))


def round_display(value: float) -> int:
    return int(Decimal(str(clamp(value))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass(frozen=True, slots=True)
class WeightedResult:
    score: float | None
    effective_weights: dict[str, float]


def weighted_result(
    values: Mapping[str, float | None], weights: Mapping[str, float]
) -> WeightedResult:
    """V2 weighted result with explicit N/A redistribution metadata."""
    included = [(name, values.get(name), weight) for name, weight in weights.items() if values.get(name) is not None]
    denominator = sum(weight for _, _, weight in included)
    if not included or denominator <= 0:
        return WeightedResult(score=None, effective_weights={})
    effective = {name: weight / denominator for name, _, weight in included}
    score = sum(float(value) * effective[name] for name, value, _ in included if value is not None)
    return WeightedResult(score=round_internal(score), effective_weights=effective)
