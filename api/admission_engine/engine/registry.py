from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from api.admission_engine.engine.enums import ConfidenceLevel, RuleSeverity
from api.admission_engine.engine.models import RuleResult


class Rule(Protocol):
    @property
    def rule_id(self) -> str: ...

    def evaluate(self, context: Mapping[str, Any]) -> RuleResult | None: ...


_SEVERITY_ORDER = {
    RuleSeverity.CRITICAL: 0,
    RuleSeverity.HIGH: 1,
    RuleSeverity.MEDIUM: 2,
    RuleSeverity.LOW: 3,
    RuleSeverity.INFO: 4,
}

_CONFIDENCE_ORDER = {
    ConfidenceLevel.HIGH: 0,
    ConfidenceLevel.MEDIUM: 1,
    ConfidenceLevel.LOW: 2,
}


def result_sort_key(result: RuleResult) -> tuple[int, float, int, int, str]:
    impact = abs(result.score_delta) if result.score_delta is not None else 0.0
    position = result.textual_position if result.textual_position is not None else 2**31 - 1
    return (
        _SEVERITY_ORDER[result.severity],
        -impact,
        _CONFIDENCE_ORDER[result.confidence],
        position,
        result.rule_id,
    )


@dataclass(slots=True)
class RuleRegistry:
    _rules: dict[str, Rule] = field(default_factory=dict)

    def register(self, rule: Rule) -> None:
        if rule.rule_id in self._rules:
            raise ValueError(f"Rule already registered: {rule.rule_id}")
        self._rules[rule.rule_id] = rule

    def extend(self, rules: Iterable[Rule]) -> None:
        for rule in rules:
            self.register(rule)

    def registered_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules))

    def evaluate(self, context: Mapping[str, Any]) -> tuple[RuleResult, ...]:
        results = (
            result
            for rule_id in sorted(self._rules)
            if (result := self._rules[rule_id].evaluate(context)) is not None
        )
        return tuple(sorted(results, key=result_sort_key))
