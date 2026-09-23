import re
from typing import Literal

from api.admission_engine.engine.scoring import weighted_score
from api.admission_engine.schemas.lor import LorEvaluationRequest, LorEvaluationResponse
from api.admission_engine.text.metrics import sentences

ACADEMIC_TRAITS = (
    "curious",
    "analytical",
    "intellectual",
    "research",
    "academic",
    "classroom",
    "problem solving",
    "critical thinking",
)
COMMUNITY_TRAITS = (
    "community",
    "collaborative",
    "mentor",
    "support",
    "team",
    "respect",
    "contribute",
)
GENERIC_PRAISE = (
    "excellent student",
    "hardworking",
    "wonderful",
    "outstanding",
    "highly recommend",
    "great person",
)
COMPARATIVE = (r"top\s+\d+%", r"among the strongest", r"one of the best", r"in my \d+ years")
EVENT_MARKERS = (
    "when",
    "during",
    "project",
    "assignment",
    "competition",
    "research",
    "semester",
    "year",
)


def evaluate_lor(request: LorEvaluationRequest) -> LorEvaluationResponse:
    text = request.text.lower()
    relationship = 30
    if request.recommender_role:
        relationship = 50
    if request.recommender_role and request.relationship_duration_months is not None:
        relationship = 70
    if request.instructional_context:
        relationship = 85
    if (
        request.instructional_context
        and request.relationship_duration_months
        and request.relationship_duration_months >= 24
    ):
        relationship = 95
    sentence_list = sentences(request.text)
    examples = sum(
        bool(re.search(r"\b\d|\b(?:when|during|after|before)\b", sentence, re.I))
        and any(marker in sentence.lower() for marker in EVENT_MARKERS)
        for sentence in sentence_list
    )
    specific = (
        25
        if examples == 0
        else 55
        if examples == 1
        else 75
        if examples == 2
        else 88
        if examples == 3
        else 95
    )
    academic = min(100, 35 + sum(text.count(trait) for trait in ACADEMIC_TRAITS) * 10)
    community = min(100, 40 + sum(text.count(trait) for trait in COMMUNITY_TRAITS) * 10)
    comparisons = sum(bool(re.search(pattern, text)) for pattern in COMPARATIVE)
    comparative = 35 if comparisons == 0 else min(95, 60 + comparisons * 15)
    generic_count = sum(text.count(phrase) for phrase in GENERIC_PRAISE)
    evidence_sentences = sum(
        any(phrase in sentence.lower() for phrase in GENERIC_PRAISE)
        and bool(re.search(r"\b(?:because|when|after|during|for example)\b", sentence, re.I))
        for sentence in sentence_list
    )
    generic_control = max(20, 100 - max(0, generic_count - evidence_sentences) * 12)
    components = {
        "relationship_context": float(relationship),
        "specific_evidence": float(specific),
        "academic_traits": float(academic),
        "community_traits": float(community),
        "comparative_evidence": float(comparative),
        "generic_praise_control": float(generic_control),
    }
    overall = (
        weighted_score(
            components,
            {
                "relationship_context": 0.20,
                "specific_evidence": 0.30,
                "academic_traits": 0.15,
                "community_traits": 0.10,
                "comparative_evidence": 0.15,
                "generic_praise_control": 0.10,
            },
        )
        or 0
    )
    rules = []
    if relationship == 30:
        rules.append("LOR-001")
    if generic_count > evidence_sentences:
        rules.append("LOR-002")
    if comparisons:
        rules.append("LOR-003")
    if examples:
        rules.append("LOR-004")
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = (
        "HIGH"
        if len(request.text.split()) >= 250
        else "MEDIUM"
        if len(request.text.split()) >= 100
        else "LOW"
    )
    return LorEvaluationResponse(
        overall_score=overall,
        display_score=round(overall),
        components=components,
        triggered_rules=rules,
        confidence=confidence,
    )
