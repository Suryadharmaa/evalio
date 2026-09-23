from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pytest

from api.admission_engine.engine.enums import ConfidenceLevel, RuleDomain, RuleSeverity
from api.admission_engine.engine.models import RuleResult
from api.admission_engine.engine.registry import RuleRegistry


@dataclass(frozen=True)
class StubRule:
    rule_id: str
    severity: RuleSeverity
    delta: float

    def evaluate(self, context: Mapping[str, Any]) -> RuleResult | None:
        if not context.get("trigger", False):
            return None
        return RuleResult(
            rule_id=self.rule_id,
            rule_version="1.0.0",
            name="Stub",
            domain=RuleDomain.ESSAY,
            category="Test",
            severity=self.severity,
            message="Triggered.",
            score_delta=self.delta,
            confidence=ConfidenceLevel.HIGH,
        )


def test_registry_returns_stable_priority_order() -> None:
    registry = RuleRegistry()
    registry.extend(
        [
            StubRule("ESSAY-003", RuleSeverity.MEDIUM, -5),
            StubRule("ESSAY-002", RuleSeverity.HIGH, -2),
            StubRule("ESSAY-001", RuleSeverity.HIGH, -10),
        ]
    )

    first = registry.evaluate({"trigger": True})
    second = registry.evaluate({"trigger": True})

    assert [result.rule_id for result in first] == ["ESSAY-001", "ESSAY-002", "ESSAY-003"]
    assert first == second


def test_registry_rejects_duplicate_rule_id() -> None:
    registry = RuleRegistry()
    rule = StubRule("ESSAY-001", RuleSeverity.INFO, 0)
    registry.register(rule)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(rule)
