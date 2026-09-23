import uuid
from pathlib import Path
from typing import Annotated, cast

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select

from api.admission_engine.application.dependencies import bearer, get_token_verifier
from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.database.models import Evaluation, EvaluationComponent, User
from api.admission_engine.database.session import get_session_factory
from api.admission_engine.engine.academic import evaluate_academic
from api.admission_engine.engine.activities import (
    evaluate_activities,
    evaluate_activity_description,
)
from api.admission_engine.engine.college import (
    audit_application,
    evaluate_college,
    evaluate_financial,
)
from api.admission_engine.engine.coursework import evaluate_coursework
from api.admission_engine.engine.essay import evaluate_essay
from api.admission_engine.engine.honors import evaluate_honor
from api.admission_engine.engine.lor import evaluate_lor
from api.admission_engine.engine.profile_strength import evaluate_profile_strength
from api.admission_engine.engine.writing_patterns import evaluate_writing_patterns
from api.admission_engine.errors import DomainError, NotFoundError, UnauthorizedError
from api.admission_engine.parsers import parse_document
from api.admission_engine.schemas.academic import AcademicEvaluationRequest
from api.admission_engine.schemas.activities import (
    ActivityDescriptionRequest,
    ActivityEvaluationRequest,
)
from api.admission_engine.schemas.college_evaluation import (
    ApplicationAuditRequest,
    CollegeEvaluationRequest,
    FinancialEvaluationRequest,
)
from api.admission_engine.schemas.coursework import CourseworkEvaluationRequest
from api.admission_engine.schemas.essay import (
    EssayEvaluationRequest,
    EssayEvaluationResponse,
    EssayType,
    SavedEssayCompareRequest,
)
from api.admission_engine.schemas.honors import HonorInput
from api.admission_engine.schemas.lor import LorEvaluationRequest
from api.admission_engine.schemas.profile_strength import ProfileStrengthRequest
from api.admission_engine.schemas.writing_patterns import WritingPatternRequest

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


def _public_essay_result(evaluation: EssayEvaluationResponse) -> dict[str, object]:
    result = evaluation.model_dump(mode="json")
    issues = cast(list[dict[str, object]], result["issues"])
    for issue in issues:
        delta = issue.get("score_delta")
        issue["score_effect"] = (
            f"{float(delta):+g} component points from this rule."
            if isinstance(delta, int | float)
            else "Finding only; no separate point adjustment."
        )
        issue["confidence"] = evaluation.confidence
        issue["methodology_link"] = "/methodology/essay"
    return result


@router.post("/academic")
def academic_evaluation(payload: AcademicEvaluationRequest, request: Request) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_academic(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/coursework")
def coursework_evaluation(
    payload: CourseworkEvaluationRequest, request: Request
) -> dict[str, object]:
    evaluation = evaluate_coursework(payload)
    return {
        "data": {"evaluation": evaluation},
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "rubric_version": evaluation.rubric_version,
        },
    }


@router.post("/activities")
def activities_evaluation(
    payload: ActivityEvaluationRequest, request: Request
) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_activities(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/activity-description")
def activity_description_evaluation(
    payload: ActivityDescriptionRequest, request: Request
) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_activity_description(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/honor")
def honor_evaluation(payload: HonorInput, request: Request) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_honor(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/essay")
def essay_evaluation(payload: EssayEvaluationRequest, request: Request) -> dict[str, object]:
    if payload.save or payload.save_raw_text:
        payload = payload.model_copy(update={"save": False, "save_raw_text": False})
    evaluation = evaluate_essay(payload)
    return {
        "data": {"evaluation": _public_essay_result(evaluation)},
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "rubric_version": evaluation.rubric_version,
        },
    }


@router.post("/essay/upload")
async def essay_upload(
    request: Request,
    file: Annotated[UploadFile, File()],
    essay_type: Annotated[EssayType, Form()] = "COMMON_APP",
    min_words: Annotated[int, Form(ge=0, le=10_000)] = 250,
    word_limit: Annotated[int, Form(ge=1, le=10_000)] = 650,
    prompt_text: Annotated[str | None, Form(max_length=10_000)] = None,
) -> dict[str, object]:
    if min_words > word_limit:
        raise DomainError("min_words cannot exceed word_limit", code="INVALID_INPUT")
    content = await file.read(4 * 1024 * 1024 + 1)
    if Path(file.filename or "").suffix.lower() not in {".txt", ".md", ".docx", ".pdf"}:
        raise DomainError(
            "Upload a TXT, Markdown, DOCX, or text-based PDF file",
            code="UNSUPPORTED_FILE",
        )
    parsed = parse_document(file.filename or "upload", content)
    evaluation = evaluate_essay(
        EssayEvaluationRequest(
            essay_type=essay_type,
            text=parsed.text,
            min_words=min_words,
            word_limit=word_limit,
            prompt_text=prompt_text,
            save=False,
        )
    )
    return {
        "data": {
            "evaluation": _public_essay_result(evaluation),
            "file": {"kind": parsed.kind, "metadata": parsed.metadata},
        },
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "rubric_version": evaluation.rubric_version,
        },
    }


@router.post("/writing-patterns")
def writing_pattern_evaluation(
    payload: WritingPatternRequest, request: Request
) -> dict[str, object]:
    evaluation = evaluate_writing_patterns(payload)
    return {
        "data": {"evaluation": evaluation},
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "rubric_version": evaluation.rubric_version,
        },
    }


@router.post("/lor")
def lor_evaluation(payload: LorEvaluationRequest, request: Request) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_lor(payload.model_copy(update={"save": False}))},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/college")
def college_evaluation(payload: CollegeEvaluationRequest, request: Request) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_college(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/financial")
def financial_evaluation(
    payload: FinancialEvaluationRequest, request: Request
) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_financial(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/application-audit")
def application_audit(payload: ApplicationAuditRequest, request: Request) -> dict[str, object]:
    return {
        "data": {"audit": audit_application(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.post("/profile-strength")
def profile_strength(payload: ProfileStrengthRequest, request: Request) -> dict[str, object]:
    return {
        "data": {"evaluation": evaluate_profile_strength(payload)},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


async def _saved_essay_summary(
    evaluation_id: uuid.UUID, user_id: uuid.UUID
) -> dict[str, object]:
    async with get_session_factory()() as session:
        evaluation = await session.scalar(
            select(Evaluation).where(
                Evaluation.id == evaluation_id,
                Evaluation.user_id == user_id,
                Evaluation.evaluation_type == "ESSAY",
            )
        )
        if evaluation is None:
            raise NotFoundError("Saved essay evaluation not found")
        components = list(
            await session.scalars(
                select(EvaluationComponent).where(
                    EvaluationComponent.evaluation_id == evaluation.id
                )
            )
        )
        return {
            "id": evaluation.id,
            "overall_score": float(evaluation.overall_score or 0),
            "display_score": evaluation.display_score,
            "confidence": evaluation.confidence,
            "components": {
                item.component_name: float(item.score) if item.score is not None else None
                for item in components
            },
        }


@router.post("/essay/compare")
async def compare_essays(
    payload: list[EssayEvaluationRequest] | SavedEssayCompareRequest,
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict[str, object]:
    if isinstance(payload, SavedEssayCompareRequest):
        if credentials is None or credentials.scheme.casefold() != "bearer":
            raise UnauthorizedError("Authentication required for saved comparisons")
        identity = get_token_verifier().verify(credentials.credentials)
        async with get_session_factory()() as session:
            user_id = await session.scalar(
                select(User.id).where(User.auth_subject == identity.subject)
            )
        if user_id is None:
            raise NotFoundError("Account not found")
        left = await _saved_essay_summary(payload.left_evaluation_id, user_id)
        right = await _saved_essay_summary(payload.right_evaluation_id, user_id)
        delta = round(
            float(cast(float | int, right["overall_score"]))
            - float(cast(float | int, left["overall_score"])),
            2,
        )
        data: dict[str, object] = {"left": left, "right": right, "overall_delta": delta}
    else:
        if len(payload) != 2:
            raise DomainError("Exactly two drafts are required", code="INVALID_INPUT")
        evaluations = [evaluate_essay(item.model_copy(update={"save": False})) for item in payload]
        delta = round(evaluations[1].overall_score - evaluations[0].overall_score, 2)
        data = {"left": evaluations[0], "right": evaluations[1], "overall_delta": delta}
    return {
        "data": data,
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }
