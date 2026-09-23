from fastapi import APIRouter, Request

from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.engine.essay_ideas import build_essay_ideas
from api.admission_engine.schemas.essay_ideas import EssayIdeaBuildRequest

router = APIRouter(prefix="/api/v1/essay-ideas", tags=["essay-ideas"])


@router.post("/build")
def build(payload: EssayIdeaBuildRequest, request: Request) -> dict[str, object]:
    result = build_essay_ideas(payload)
    return {
        "data": {"result": result},
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "builder_version": result.builder_version,
        },
    }
