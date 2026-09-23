import asyncio
import uuid
from decimal import Decimal
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from api.admission_engine.database.models import (
    EssayMetric,
    Evaluation,
    EvaluationComponent,
    TriggeredRule,
)
from api.admission_engine.database.models import TestScore as ScoreRecord
from api.admission_engine.engine.college import evaluate_college
from api.admission_engine.engine.essay import evaluate_essay
from api.admission_engine.routers.profile_data import (
    cds_application_component,
    normalized_triggered_rules,
    persist_evaluation,
    select_college_test,
)
from api.admission_engine.schemas.college_evaluation import CollegeEvaluationRequest
from api.admission_engine.schemas.essay import EssayEvaluationRequest


def test_structured_issue_evidence_is_preserved_and_not_duplicated() -> None:
    data = {
        "issues": [
            {
                "rule_id": "ESS-001",
                "severity": "HIGH",
                "message": "Essay exceeds its word limit.",
                "evidence": {"word_count": 700, "word_limit": 650},
                "score_delta": -10.0,
            }
        ],
        "triggered_rules": ["ESS-001", "ESS-002"],
    }

    rules = normalized_triggered_rules(data, evaluation_type="ESSAY", confidence="HIGH")

    assert [rule["rule_id"] for rule in rules] == ["ESS-001", "ESS-002"]
    assert rules[0]["severity"] == "HIGH"
    assert rules[0]["evidence"] == {"word_count": 700, "word_limit": 650}
    assert rules[1]["message"] == "Deterministic rule triggered."


def test_dict_triggered_rule_is_supported() -> None:
    rules = normalized_triggered_rules(
        {
            "triggered_rules": [
                {
                    "rule_id": "ACA-001",
                    "severity": "LOW",
                    "title": "Limited terms",
                    "evidence": {"term_count": 1},
                }
            ]
        },
        evaluation_type="ACADEMIC",
        confidence="LOW",
    )

    assert rules[0]["message"] == "Limited terms"
    assert rules[0]["confidence"] == "LOW"


def test_cds_factor_labels_map_only_to_measurable_components() -> None:
    assert cds_application_component("Rigor of secondary school record") == "academics"
    assert cds_application_component("Standardized test scores") == "testing"
    assert cds_application_component("Application essay") == "essay"
    assert cds_application_component("Recommendation(s)") == "recommendations"
    assert cds_application_component("Extracurricular activities") == "activities"
    assert cds_application_component("Talent/ability") == "honors"
    assert cds_application_component("Character/personal qualities") is None


def test_college_test_selection_ignores_english_proficiency_scores() -> None:
    english = ScoreRecord(test_type="IELTS", composite_score=Decimal("8.0"))
    sat = ScoreRecord(test_type="SAT", composite_score=Decimal("1450"))

    assert select_college_test([english, sat]) is sat


def test_saved_essay_persists_metrics_and_structured_rules() -> None:
    class RecordingSession:
        def __init__(self) -> None:
            self.items: list[object] = []

        def add(self, item: object) -> None:
            self.items.append(item)

        async def flush(self) -> None:
            for item in self.items:
                if isinstance(item, Evaluation) and item.id is None:
                    item.id = uuid.uuid4()

    session = RecordingSession()
    text = " ".join(["evidence"] * 30)
    result = evaluate_essay(
        EssayEvaluationRequest(text=text, min_words=1, word_limit=10)
    )
    essay_id = uuid.uuid4()

    asyncio.run(
        persist_evaluation(
            cast(AsyncSession, session),
            user_id=uuid.uuid4(),
            profile_id=uuid.uuid4(),
            evaluation_type="ESSAY",
            input_data={"content_hash": "a" * 64},
            result=result,
            subject_entity_id=essay_id,
        )
    )

    metric = next(item for item in session.items if isinstance(item, EssayMetric))
    rules = [item for item in session.items if isinstance(item, TriggeredRule)]
    assert metric.essay_id == essay_id
    assert metric.word_count == 30
    assert rules
    assert any(rule.evidence for rule in rules)


def test_college_application_strength_and_components_are_persisted() -> None:
    class RecordingSession:
        def __init__(self) -> None:
            self.items: list[object] = []

        def add(self, item: object) -> None:
            self.items.append(item)

        async def flush(self) -> None:
            for item in self.items:
                if isinstance(item, Evaluation) and item.id is None:
                    item.id = uuid.uuid4()

    session = RecordingSession()
    result = evaluate_college(
        CollegeEvaluationRequest(
            academic_strength=90,
            application_components={"activities": 70},
            cds_importance={"academics": "VERY_IMPORTANT", "activities": "IMPORTANT"},
            acceptance_rate=0.30,
            profile_completeness=35,
            source_freshness_points=25,
            college_data_completeness=20,
            metric_reliability=20,
        )
    )

    row = asyncio.run(
        persist_evaluation(
            cast(AsyncSession, session),
            user_id=uuid.uuid4(),
            profile_id=uuid.uuid4(),
            evaluation_type="COLLEGE",
            input_data={"college_id": "example"},
            result=result,
            college_id=uuid.uuid4(),
        )
    )

    components = [item for item in session.items if isinstance(item, EvaluationComponent)]
    assert row.overall_score == result.application_strength
    assert row.display_score == round(result.application_strength or 0)
    assert {item.component_name for item in components} == {"academics", "activities"}
