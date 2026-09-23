from fastapi import APIRouter, Request

from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.engine.lor_builder import build_lor_framework
from api.admission_engine.schemas.lor_builder import LorBuildRequest

router = APIRouter(prefix="/api/v1/lor", tags=["lor-builder"])


@router.post("/build")
def build(payload: LorBuildRequest, request: Request) -> dict[str, object]:
    result = build_lor_framework(payload)
    return {
        "data": {"result": result},
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "builder_version": result.builder_version,
        },
    }
