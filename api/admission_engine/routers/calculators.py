from fastapi import APIRouter, Request

from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.engine.gpa import calculate_gpa
from api.admission_engine.schemas.gpa import GpaCalculationRequest

router = APIRouter(prefix="/api/v1/calculators", tags=["calculators"])


@router.post("/gpa")
def gpa(payload: GpaCalculationRequest, request: Request) -> dict[str, object]:
    result = calculate_gpa(payload)
    return {"data": {"result": result}, "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION, "calculator_version": result.calculator_version}}
