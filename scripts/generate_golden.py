"""Regenerate deterministic fixture outputs after an intentional rubric version change."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
GOLDEN = FIXTURES / "golden"


def generate(
    fixture_name: str,
    schema: type[BaseModel],
    evaluator: Callable[[Any], BaseModel],
) -> None:
    records = json.loads((FIXTURES / f"{fixture_name}.json").read_text(encoding="utf-8"))
    outputs = []
    for record in records:
        payload = dict(record)
        fixture_id = payload.pop("id")
        outputs.append(
            {
                "id": fixture_id,
                "result": evaluator(schema.model_validate(payload)).model_dump(mode="json"),
            }
        )
    (GOLDEN / f"{fixture_name}.json").write_text(
        json.dumps(outputs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    generate("academics", AcademicEvaluationRequest, evaluate_academic)
    generate("activities", ActivityEvaluationRequest, evaluate_activities)
    generate("essays", EssayEvaluationRequest, evaluate_essay)
    generate("honors", HonorInput, evaluate_honor)
    generate("lors", LorEvaluationRequest, evaluate_lor)
    generate("colleges", CollegeEvaluationRequest, evaluate_college)


if __name__ == "__main__":
    main()
