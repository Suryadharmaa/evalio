"""Public hybrid essay review endpoints."""

from fastapi import APIRouter, Request

from api.admission_engine.application.essay_review import deep_review, review_essay
from api.admission_engine.schemas.essay_review import DeepReviewRequest, EssayReviewRequest

router = APIRouter(prefix="/api/v1/essay-review", tags=["essay-review"])


@router.post("")
async def analyze(payload: EssayReviewRequest, request: Request) -> dict[str, object]:
    return {
        "data": await review_essay(payload.essay, refresh=payload.refresh),
        "meta": {"request_id": request.state.request_id},
    }


@router.post("/deep")
async def analyze_deep(payload: DeepReviewRequest, request: Request) -> dict[str, object]:
    return {
        "data": await deep_review(payload.analysis_id, payload.essay),
        "meta": {"request_id": request.state.request_id},
    }
