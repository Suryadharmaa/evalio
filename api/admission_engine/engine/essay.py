from collections import Counter
from typing import Literal

from api.admission_engine.engine.scoring import clamp, weighted_score
from api.admission_engine.schemas.essay import (
    EssayEvaluationRequest,
    EssayEvaluationResponse,
    EssayIssue,
    EssayMetrics,
)
from api.admission_engine.text.metrics import TextMetrics, analyze_text, sentences

ESSAY_WEIGHTS = {
    "compliance": 0.10,
    "clarity": 0.15,
    "structure": 0.15,
    "specificity": 0.15,
    "reflection": 0.15,
    "voice": 0.10,
    "sentence_variety": 0.10,
    "style_hygiene": 0.10,
}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


def _tiered_penalty(difference: int) -> int:
    return 15 if difference <= 10 else 30 if difference <= 25 else 50 if difference <= 50 else 80


def _issue(
    rule_id: str,
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
    title: str,
    message: str,
    evidence: dict[str, object],
    delta: float | None = None,
) -> EssayIssue:
    return EssayIssue(
        rule_id=rule_id,
        severity=severity,
        title=title,
        message=message,
        evidence=evidence,
        score_delta=delta,
    )


def _reflection(metrics: TextMetrics) -> tuple[float, float, set[int]]:
    effective = sum(
        1 + (0.5 if count >= 2 else 0) + (0.25 if count >= 3 else 0)
        for count in metrics.reflection_counts.values()
    )
    density = effective / metrics.word_count * 100 if metrics.word_count else 0
    base = (
        25
        if density == 0
        else 40
        if density < 0.5
        else 55
        if density < 1
        else 70
        if density < 1.5
        else 80
        if density < 2
        else 90
        if density < 3
        else 95
    )
    quartiles: set[int] = {
        min(3, int(position / max(1, metrics.word_count) * 4))
        for position in metrics.reflection_positions
    }
    bonus = 5 if len(quartiles) >= 3 else 3 if len(quartiles) >= 2 else 0
    return clamp(base + bonus), round(density, 3), quartiles


def evaluate_essay(request: EssayEvaluationRequest) -> EssayEvaluationResponse:
    metrics = analyze_text(request.text)
    issues: list[EssayIssue] = []
    compliance = 100.0
    if request.word_limit is not None and metrics.word_count > request.word_limit:
        difference = metrics.word_count - request.word_limit
        penalty = _tiered_penalty(difference)
        compliance -= penalty
        issues.append(
            _issue(
                "ESSAY-001",
                "CRITICAL",
                "Maximum word limit exceeded",
                f"Essay exceeds the {request.word_limit}-word limit by {difference} words.",
                {
                    "word_count": metrics.word_count,
                    "max_words": request.word_limit,
                    "difference": difference,
                },
                -penalty,
            )
        )
    if request.min_words is not None and metrics.word_count < request.min_words:
        difference = request.min_words - metrics.word_count
        penalty = _tiered_penalty(difference)
        compliance -= penalty
        issues.append(
            _issue(
                "ESSAY-002",
                "CRITICAL",
                "Below minimum word count",
                f"Essay is {difference} words below the minimum.",
                {
                    "word_count": metrics.word_count,
                    "min_words": request.min_words,
                    "difference": difference,
                },
                -penalty,
            )
        )

    clarity = 100.0
    moderate = sum(31 <= length <= 40 for length in metrics.sentence_lengths)
    long = sum(41 <= length <= 50 for length in metrics.sentence_lengths)
    extreme = sum(length > 50 for length in metrics.sentence_lengths)
    clarity -= min(8, moderate) + min(10, long * 2) + min(16, extreme * 4)
    if moderate:
        issues.append(
            _issue(
                "ESSAY-004",
                "LOW",
                "Moderately long sentences",
                f"{moderate} sentences contain 31–40 words.",
                {"count": moderate},
                -min(8, moderate),
            )
        )
    if long or extreme:
        issues.append(
            _issue(
                "ESSAY-003",
                "MEDIUM",
                "Very long sentences",
                f"{long + extreme} sentences contain more than 40 words.",
                {"count": long + extreme},
                -(min(10, long * 2) + min(16, extreme * 4)),
            )
        )
    clarity -= min(10, sum(metrics.filler_counts.values()))
    passive_ratio = (
        metrics.passive_sentence_count / metrics.sentence_count if metrics.sentence_count else 0
    )
    if passive_ratio > 0.2:
        passive_penalty = min(8, round(passive_ratio * 20))
        clarity -= passive_penalty
        issues.append(
            _issue(
                "ESSAY-029",
                "LOW",
                "Possible passive pattern",
                "A deterministic heuristic found frequent passive constructions.",
                {"sentence_ratio": round(passive_ratio, 3)},
                -passive_penalty,
            )
        )
    if metrics.flesch_reading_ease is not None:
        readability_penalty = (
            12
            if metrics.flesch_reading_ease < 20
            else 8
            if metrics.flesch_reading_ease < 35
            else 4
            if metrics.flesch_reading_ease < 50
            else 0
        )
        clarity -= readability_penalty
        if readability_penalty:
            rule = (
                "ESSAY-026"
                if readability_penalty == 12
                else "ESSAY-027"
                if readability_penalty == 8
                else "ESSAY-028"
            )
            issues.append(
                _issue(
                    rule,
                    "MEDIUM" if readability_penalty == 12 else "LOW",
                    "Readability difficulty",
                    "Sentence and syllable patterns may make the draft difficult to read.",
                    {"flesch_reading_ease": metrics.flesch_reading_ease},
                    -readability_penalty,
                )
            )

    structure = 70.0
    if 3 <= metrics.paragraph_count <= 8:
        structure += 8
    if (
        metrics.paragraph_lengths
        and max(metrics.paragraph_lengths) / max(1, metrics.word_count) <= 0.35
        and sorted(metrics.paragraph_lengths)[len(metrics.paragraph_lengths) // 2] >= 25
    ):
        structure += 6
    if (
        metrics.paragraph_lengths
        and metrics.paragraph_lengths[0] / max(1, metrics.word_count) <= 0.35
    ):
        structure += 4
    if metrics.paragraph_count >= 2:
        structure += 4
    if len(metrics.transition_types) >= 3:
        structure += 4
    if metrics.paragraph_count == 1 and metrics.word_count >= 250:
        structure -= 20
        issues.append(
            _issue(
                "ESSAY-006",
                "HIGH",
                "One-paragraph essay",
                "Long essays benefit from visible paragraph structure.",
                {"paragraph_count": 1},
                -20,
            )
        )
    if (
        metrics.paragraph_lengths
        and max(metrics.paragraph_lengths) / max(1, metrics.word_count) > 0.45
    ):
        structure -= 10
        issues.append(
            _issue(
                "ESSAY-005",
                "MEDIUM",
                "Extreme paragraph dominance",
                "One paragraph contains more than 45% of the essay.",
                {"largest_paragraph_words": max(metrics.paragraph_lengths)},
                -10,
            )
        )
    if sum(length < 15 for length in metrics.paragraph_lengths) >= 3:
        structure -= 5

    specificity_density = (
        metrics.specificity_count / metrics.word_count * 100 if metrics.word_count else 0
    )
    specificity = (
        35
        if specificity_density <= 0.5
        else 50
        if specificity_density <= 1
        else 65
        if specificity_density <= 2
        else 80
        if specificity_density <= 3
        else 90
        if specificity_density <= 4
        else 95
    )
    if len(metrics.specificity_categories) >= 4:
        specificity += 5
    if specificity_density < 0.5 and metrics.word_count >= 250:
        issues.append(
            _issue(
                "ESSAY-014",
                "MEDIUM",
                "Low specificity signal density",
                "Few measurable specificity signals were detected.",
                {"signals_per_100_words": round(specificity_density, 3)},
            )
        )

    reflection, reflection_density, quartiles = _reflection(metrics)
    if reflection_density == 0 and metrics.word_count >= 250:
        issues.append(
            _issue(
                "ESSAY-013",
                "MEDIUM",
                "No reflection signals",
                "No configured reflection markers were detected.",
                {},
            )
        )
    for marker, count in metrics.reflection_counts.items():
        if count >= 3:
            issues.append(
                _issue(
                    "ESSAY-011",
                    "MEDIUM",
                    "Repeated reflection marker",
                    f"“{marker}” appears {count} times and has diminishing value.",
                    {"marker": marker, "count": count},
                )
            )

    lengths = metrics.sentence_lengths
    sentence_variety = 85.0
    bands = Counter(
        0 if length < 8 else 1 if length <= 20 else 2 if length <= 35 else 3 for length in lengths
    )
    if metrics.sentence_length_stddev >= 7 and len(bands) >= 3:
        sentence_variety += 10
    if lengths and max(bands.values()) / len(lengths) > 0.6:
        sentence_variety -= 15
    if lengths and sum(length > 35 for length in lengths) / len(lengths) > 0.25:
        sentence_variety -= 15
    if lengths and sum(length < 8 for length in lengths) / len(lengths) > 0.35:
        sentence_variety -= 10

    sentence_list = sentences(request.text)
    openings = Counter(
        " ".join(sentence.lower().split()[:3]) for sentence in sentence_list if sentence
    )
    repeated_opening = bool(
        sentence_list
        and len(sentence_list) >= 10
        and max(openings.values(), default=0) / len(sentence_list) >= 0.2
    )
    generic_density = (
        sum(metrics.generic_counts.values()) / metrics.word_count * 100 if metrics.word_count else 0
    )
    voice = (
        60
        + (8 if "i" in request.text.lower().split() else 0)
        + (8 if sentence_variety >= 85 else 0)
        + (4 if metrics.dialogue_present else 0)
        + (4 if len(metrics.transition_types) >= 3 else 0)
        + (2 if "'" in request.text or "’" in request.text else 0)
    )
    if generic_density >= 1.5:
        voice -= 10
    if repeated_opening:
        voice -= 8

    style = (
        100
        - min(15, sum(metrics.cliche_counts.values()) * 3)
        - min(12, sum(metrics.filler_counts.values()) * 2)
        - min(12, len(metrics.repeated_phrases) * 2)
    )
    for phrase, count in metrics.cliche_counts.items():
        issues.append(
            _issue(
                "ESSAY-008",
                "LOW",
                "Cliché phrase detected",
                f"Possible cliché detected: “{phrase}”.",
                {"phrase": phrase, "count": count},
                -min(15, count * 3),
            )
        )
    for phrase, count in metrics.repeated_phrases.items():
        issues.append(
            _issue(
                "ESSAY-010",
                "MEDIUM",
                "Repeated phrase",
                f"“{phrase}” appears {count} times.",
                {"phrase": phrase, "count": count},
                -2,
            )
        )

    components = {
        "compliance": clamp(compliance),
        "clarity": clamp(clarity),
        "structure": clamp(structure),
        "specificity": clamp(specificity),
        "reflection": clamp(reflection),
        "voice": clamp(voice),
        "sentence_variety": clamp(sentence_variety),
        "style_hygiene": clamp(style),
    }
    overall = weighted_score(components, ESSAY_WEIGHTS) or 0
    issues.sort(
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            -(abs(item.score_delta) if item.score_delta else 0),
            item.rule_id,
        )
    )
    label = (
        "Exceptional internal signal"
        if overall >= 90
        else "Strong"
        if overall >= 80
        else "Competitive"
        if overall >= 70
        else "Moderate"
        if overall >= 60
        else "Limited"
        if overall >= 50
        else "Weak / insufficient signal"
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = (
        "LOW" if metrics.word_count < 50 else "MEDIUM" if metrics.word_count < 150 else "HIGH"
    )
    return EssayEvaluationResponse(
        overall_score=overall,
        display_score=round(overall),
        label=label,
        confidence=confidence,
        components=components,
        metrics=EssayMetrics(
            word_count=metrics.word_count,
            character_count=metrics.character_count,
            sentence_count=metrics.sentence_count,
            paragraph_count=metrics.paragraph_count,
            average_sentence_length=metrics.average_sentence_length,
            median_sentence_length=metrics.median_sentence_length,
            sentence_length_stddev=metrics.sentence_length_stddev,
            flesch_reading_ease=metrics.flesch_reading_ease,
            lexical_diversity=metrics.lexical_diversity,
            specificity_density=round(specificity_density, 3),
            reflection_density=reflection_density,
        ),
        issues=issues,
        triggered_rules=[item.rule_id for item in issues],
    )
