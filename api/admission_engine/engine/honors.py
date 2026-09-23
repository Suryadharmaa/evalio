from typing import Literal

from api.admission_engine.schemas.honors import HonorInput, HonorScore


def evaluate_honor(honor: HonorInput) -> HonorScore:
    rules: list[str] = ["HON-003"]
    scope = (
        None
        if honor.scope is None
        else {
            "SCHOOL": 8,
            "LOCAL": 12,
            "REGIONAL": 18,
            "STATE": 22,
            "NATIONAL": 27,
            "INTERNATIONAL": 30,
        }[honor.scope]
    )
    if scope is None:
        rules.append("HON-001")
    if (
        honor.scope == "INTERNATIONAL"
        and honor.organizer is None
        and honor.countries_represented is None
    ):
        scope = min(scope or 27, 27)
        rules.append("HON-004")
    if honor.selection_rate is None:
        selectivity = 8
        rules.append("HON-002")
    else:
        rate = honor.selection_rate
        selectivity = (
            25
            if rate <= 0.01
            else 23
            if rate <= 0.05
            else 20
            if rate <= 0.10
            else 15
            if rate <= 0.25
            else 10
            if rate <= 0.50
            else 5
        )
    placement = {
        "PARTICIPANT": 5,
        "HONORABLE_MENTION": 8,
        "TOP_10": 12,
        "TOP_5": 15,
        "THIRD": 17,
        "SECOND": 18,
        "FIRST": 20,
    }[honor.placement]
    recurrence = min(10, 4 + (honor.repeat_count - 1) * 2)
    available = [
        (scope, 30),
        (selectivity, 25),
        (placement, 20),
        (honor.academic_relevance, 15),
        (recurrence, 10),
    ]
    denominator = sum(weight for value, weight in available if value is not None)
    overall = round(
        sum(float(value) for value, _ in available if value is not None) / denominator * 100, 2
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = (
        "LOW" if scope is None else "MEDIUM" if honor.selection_rate is None else "HIGH"
    )
    return HonorScore(
        scope=scope,
        selectivity=selectivity,
        placement=placement,
        academic_relevance=honor.academic_relevance,
        recurrence=recurrence,
        overall_score=overall,
        display_score=round(overall),
        confidence=confidence,
        triggered_rules=rules,
    )
