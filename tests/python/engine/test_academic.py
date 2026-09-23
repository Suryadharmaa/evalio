from api.admission_engine.engine.academic import evaluate_academic
from api.admission_engine.schemas.academic import AcademicEvaluationRequest


def test_academic_evaluation_is_deterministic_and_redistributes_missing_context() -> None:
    payload = AcademicEvaluationRequest.model_validate(
        {
            "terms": [
                {"term_order": 1, "average_grade": 86},
                {"term_order": 2, "average_grade": 87},
                {"term_order": 3, "average_grade": 88},
            ],
            "scale_min": 0,
            "scale_max": 100,
            "rigor_evidence": {
                "highest_level_core_areas": 4,
                "relevant_core_areas": 5,
                "core_coverage": "ALL",
                "advanced_taken": 4,
                "advanced_opportunities": 5,
                "progression": "INCREASING",
                "major_preparation": "STRONG",
            },
        }
    )

    assert evaluate_academic(payload) == evaluate_academic(payload)
    assert evaluate_academic(payload).components.trend == 90
