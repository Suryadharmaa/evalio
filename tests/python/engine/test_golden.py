import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from api.admission_engine.engine.academic import evaluate_academic
from api.admission_engine.engine.activities import evaluate_activities
from api.admission_engine.engine.college import evaluate_college
from api.admission_engine.engine.essay import evaluate_essay
from api.admission_engine.engine.honors import evaluate_honor
from api.admission_engine.engine.lor import evaluate_lor
from api.admission_engine.schemas.academic import AcademicEvaluationRequest
from api.admission_engine.schemas.activities import ActivityEvaluationRequest
from api.admission_engine.schemas.college_evaluation import CollegeEvaluationRequest
from api.admission_engine.schemas.essay import EssayEvaluationRequest
from api.admission_engine.schemas.honors import HonorInput
from api.admission_engine.schemas.lor import LorEvaluationRequest

FIXTURES = Path("tests/fixtures")


@pytest.mark.parametrize(
    ("name", "schema", "evaluator"),
    [
        ("academics", AcademicEvaluationRequest, evaluate_academic),
        ("activities", ActivityEvaluationRequest, evaluate_activities),
        ("essays", EssayEvaluationRequest, evaluate_essay),
        ("honors", HonorInput, evaluate_honor),
        ("lors", LorEvaluationRequest, evaluate_lor),
        ("colleges", CollegeEvaluationRequest, evaluate_college),
    ],
)
def test_golden_outputs(
    name: str, schema: type[BaseModel], evaluator: Callable[[Any], BaseModel]
) -> None:
    inputs = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURES / "golden" / f"{name}.json").read_text(encoding="utf-8"))
    actual = []
    for record in inputs:
        payload = dict(record)
        fixture_id = payload.pop("id")
        result = evaluator(schema.model_validate(payload)).model_dump(mode="json")
        actual.append({"id": fixture_id, "result": result})
    assert actual == expected
