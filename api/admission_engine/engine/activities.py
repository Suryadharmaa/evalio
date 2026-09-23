import re

from api.admission_engine.engine.scoring import weighted_score
from api.admission_engine.schemas.activities import (
    ActivityDescriptionRequest,
    ActivityDescriptionResponse,
    ActivityEvaluationRequest,
    ActivityEvaluationResponse,
    ActivityInput,
    ActivityScores,
)

STRONG_ACTIONS = frozenset(
    {
        "built",
        "created",
        "designed",
        "directed",
        "founded",
        "grew",
        "implemented",
        "launched",
        "led",
        "managed",
        "organized",
        "produced",
        "raised",
        "researched",
        "taught",
        "trained",
    }
)
WEAK_PHRASES = ("participated in", "helped with", "was involved in", "was responsible for")
IMPACT_WORDS = frozenset(
    {
        "users",
        "members",
        "customers",
        "revenue",
        "raised",
        "participants",
        "downloads",
        "events",
        "students",
        "families",
    }
)


def _impact(activity: ActivityInput) -> int:
    if activity.impact_level == "VERIFIABLE_EXCEPTIONAL":
        return 25
    if activity.people_impacted is not None:
        count = activity.people_impacted
        return (
            22
            if count >= 1_000
            else 19
            if count >= 200
            else 15
            if count >= 50
            else 11
            if count >= 10
            else 8
            if count > 1
            else 5
        )
    return {"NONE": 2, "SELF": 5, "SMALL_GROUP": 8, "VERIFIABLE_EXCEPTIONAL": 25}[
        activity.impact_level
    ]


def evaluate_activity(activity: ActivityInput) -> ActivityScores:
    leadership = {
        "PARTICIPANT": 2,
        "INFORMAL": 6,
        "OPERATIONAL": 10,
        "LEAD": 14,
        "EXECUTIVE": 17,
        "FOUNDER": 18,
    }[activity.leadership_level]
    if activity.leadership_level == "FOUNDER":
        leadership = (
            20
            if activity.founder_responsibility_evidence and activity.sustained_operations
            else 18
            if activity.founder_responsibility_evidence
            else 10
        )
    duration = (
        15
        if activity.duration_months >= 36
        else 13
        if activity.duration_months >= 24
        else 11
        if activity.duration_months >= 12
        else 8
        if activity.duration_months >= 6
        else 5
        if activity.duration_months >= 2
        else 2
    )
    initiative = {
        "ASSIGNED": 2,
        "OCCASIONAL": 5,
        "IMPROVED": 9,
        "STARTED_PROJECT": 12,
        "CREATED_PROGRAM": 15,
    }[activity.initiative_level]
    if activity.leadership_level == "FOUNDER" and not activity.founder_responsibility_evidence:
        initiative = min(initiative, 8)
    time = (
        10
        if activity.hours_per_week >= 11
        else 8
        if activity.hours_per_week >= 6
        else 6
        if activity.hours_per_week >= 3
        else 4
        if activity.hours_per_week >= 1
        else 2
    )
    recognition = {
        "NONE": 1,
        "SCHOOL_LOCAL": 3,
        "REGIONAL": 5,
        "STATE": 7,
        "NATIONAL": 9,
        "INTERNATIONAL": 10,
    }[activity.recognition_scope]
    progression = {"NONE": 1, "SOME": 3, "CLEAR": 4, "MULTIPLE": 5}[activity.progression_level]
    parts = (_impact(activity), leadership, duration, initiative, time, recognition, progression)
    return ActivityScores(
        impact=parts[0],
        leadership=parts[1],
        duration=parts[2],
        initiative=parts[3],
        time_commitment=parts[4],
        recognition=parts[5],
        progression=parts[6],
        total=sum(parts),
    )


def evaluate_activities(request: ActivityEvaluationRequest) -> ActivityEvaluationResponse:
    individual = [evaluate_activity(activity) for activity in request.activities]
    ranked = sorted((score.total for score in individual), reverse=True)
    base_weights = [0.30, 0.25, 0.20, 0.15]
    values: list[float] = list(ranked[:4])
    weights = base_weights[: len(values)]
    if len(ranked) >= 5:
        values.append(sum(ranked[4:]) / len(ranked[4:]))
        weights.append(0.10)
    portfolio = round(
        sum(value * weight for value, weight in zip(values, weights, strict=True)) / sum(weights), 2
    )
    total_hours = sum(activity.hours_per_week for activity in request.activities)
    warnings = (
        ["Reported weekly commitments exceed 70 hours; review overlapping entries."]
        if total_hours > 70
        else []
    )
    return ActivityEvaluationResponse(
        individual_scores=individual,
        portfolio_score=portfolio,
        display_score=round(portfolio),
        warnings=warnings,
    )


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def evaluate_activity_description(
    request: ActivityDescriptionRequest,
) -> ActivityDescriptionResponse:
    description_tokens = _tokens(request.description)
    usage = len(request.description) / request.character_limit
    efficiency = (
        20
        if usage > 1
        else 100
        if usage >= 0.9
        else 90
        if usage >= 0.8
        else 80
        if usage >= 0.65
        else 68
        if usage >= 0.5
        else 55
    )
    first_action = next(
        (index for index, token in enumerate(description_tokens) if token in STRONG_ACTIONS), None
    )
    weak_dominant = request.description.lower().startswith(WEAK_PHRASES)
    action = (
        95
        if first_action is not None and first_action < 5
        else 85
        if first_action is not None and first_action < 10
        else 72
        if first_action is not None
        else 55
        if weak_dominant
        else 35
    )
    has_number = bool(re.search(r"\b\d[\d,.]*\b", request.description))
    has_impact_context = any(token in IMPACT_WORDS for token in description_tokens)
    impact = (
        95
        if has_number and has_impact_context
        else 82
        if has_impact_context
        else 70
        if first_action is not None
        else 52
        if description_tokens
        else 35
    )
    specificity = (
        95
        if has_number
        and (
            (
                bool(request.organization.strip())
                and request.organization.lower() in request.description.lower()
            )
            or has_impact_context
        )
        else 82
        if has_number or has_impact_context
        else 55
    )
    title_tokens = set(_tokens(request.position_title))
    opening_tokens = set(_tokens(request.description[:30]))
    overlap = len(title_tokens & opening_tokens) / len(title_tokens) if title_tokens else 0
    redundancy = (
        100
        if overlap < 0.2
        else 90
        if overlap < 0.4
        else 75
        if overlap < 0.6
        else 55
        if overlap < 0.8
        else 40
    )
    components = {
        "character_efficiency": efficiency,
        "action_clarity": action,
        "impact_evidence": impact,
        "specificity": specificity,
        "redundancy_control": redundancy,
    }
    overall = (
        weighted_score(
            components,
            {
                "character_efficiency": 0.20,
                "action_clarity": 0.25,
                "impact_evidence": 0.25,
                "specificity": 0.15,
                "redundancy_control": 0.15,
            },
        )
        or 0
    )
    rules = []
    if usage > 1:
        rules.append("ACT-009")
    if usage < 0.5:
        rules.append("ACT-010")
    if overlap >= 0.6:
        rules.append("ACT-001")
    if first_action is not None and first_action < 5:
        rules.append("ACT-002")
    if has_number and has_impact_context:
        rules.append("ACT-004")
    return ActivityDescriptionResponse(
        overall_score=overall,
        display_score=round(overall),
        components=components,
        triggered_rules=rules,
    )
