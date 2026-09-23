from dataclasses import dataclass

from api.admission_engine.config import V2_RUBRIC_VERSIONS


@dataclass(frozen=True, slots=True)
class V2RuleDescriptor:
    rule_id: str
    domain: str
    rubric_version: str


_RULE_GROUPS = {
    "ACAD2": ("academic", 7),
    "RIGOR2": ("coursework", 5),
    "TEST2": ("testing", 5),
    "ACT2": ("activity", 10),
    "ACTDESC2": ("activity_description", 5),
    "HON2": ("honor", 5),
    "ESSAY2": ("essay", 20),
    "WPAT2": ("writing_patterns", 6),
    "LOR2": ("lor", 7),
    "COL2": ("college", 10),
    "FIN2": ("financial", 6),
    "SCH2": ("scholarship", 4),
    "APP2": ("application", 3),
    "CONF2": ("confidence", 5),
}


def _build_registry() -> dict[str, V2RuleDescriptor]:
    registry: dict[str, V2RuleDescriptor] = {}
    for prefix, (domain, count) in _RULE_GROUPS.items():
        for number in range(1, count + 1):
            rule_id = f"{prefix}-{number:03d}"
            if rule_id in registry:
                raise RuntimeError(f"Duplicate V2 rule ID: {rule_id}")
            registry[rule_id] = V2RuleDescriptor(
                rule_id=rule_id,
                domain=domain,
                rubric_version=V2_RUBRIC_VERSIONS[domain],
            )
    return registry


V2_RULE_REGISTRY = _build_registry()
