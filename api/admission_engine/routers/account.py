from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select

from api.admission_engine.application.dependencies import (
    CurrentUserDependency,
    SessionDependency,
    get_identity,
)
from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.database.models import (
    AcademicTerm,
    Activity,
    ApplicantProfile,
    ApplicationMaterialStatus,
    Course,
    Essay,
    EssayMetric,
    Evaluation,
    EvaluationComponent,
    Honor,
    Recommendation,
    SavedReport,
    SchoolContext,
    TargetCollege,
    TestScore,
    TriggeredRule,
    User,
)
from api.admission_engine.errors import DomainError
from api.admission_engine.schemas.profiles import ProfileRead

router = APIRouter(prefix="/api/v1/account", tags=["account"], dependencies=[Depends(get_identity)])


def row_dict(row: object) -> dict[str, object]:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}  # type: ignore[attr-defined]


@router.get("/export")
async def export_account(
    request: Request, session: SessionDependency, user: CurrentUserDependency
) -> Response:
    profiles = list(
        await session.scalars(select(ApplicantProfile).where(ApplicantProfile.user_id == user.id))
    )
    profile_ids = [profile.id for profile in profiles]
    profile_models = {
        "academic_terms": AcademicTerm,
        "courses": Course,
        "school_context": SchoolContext,
        "test_scores": TestScore,
        "activities": Activity,
        "honors": Honor,
        "targets": TargetCollege,
        "application_material_status": ApplicationMaterialStatus,
    }
    exported: dict[str, object] = {}
    for name, model in profile_models.items():
        rows = (
            list(await session.scalars(select(model).where(model.profile_id.in_(profile_ids))))  # type: ignore[attr-defined]
            if profile_ids
            else []
        )
        exported[name] = [row_dict(row) for row in rows]
    for name, model in {
        "essays": Essay,
        "recommendations": Recommendation,
        "evaluations": Evaluation,
        "reports": SavedReport,
    }.items():
        rows = list(await session.scalars(select(model).where(model.user_id == user.id)))  # type: ignore[attr-defined]
        exported[name] = [row_dict(row) for row in rows]
    essay_ids = [
        row.id
        for row in await session.scalars(select(Essay).where(Essay.user_id == user.id))
    ]
    evaluation_ids = [
        row.id
        for row in await session.scalars(select(Evaluation).where(Evaluation.user_id == user.id))
    ]
    exported["essay_metrics"] = [
        row_dict(row)
        for row in (
            await session.scalars(select(EssayMetric).where(EssayMetric.essay_id.in_(essay_ids)))
            if essay_ids
            else []
        )
    ]
    exported["evaluation_components"] = [
        row_dict(row)
        for row in (
            await session.scalars(
                select(EvaluationComponent).where(
                    EvaluationComponent.evaluation_id.in_(evaluation_ids)
                )
            )
            if evaluation_ids
            else []
        )
    ]
    exported["triggered_rules"] = [
        row_dict(row)
        for row in (
            await session.scalars(
                select(TriggeredRule).where(TriggeredRule.evaluation_id.in_(evaluation_ids))
            )
            if evaluation_ids
            else []
        )
    ]
    payload = {
        "export_version": "1.0.0",
        "account": {
            "id": str(user.id),
            "email_snapshot": user.email_snapshot,
            "created_at": user.created_at.isoformat(),
        },
        "profiles": [
            ProfileRead.model_validate(profile).model_dump(mode="json") for profile in profiles
        ],
        **exported,
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }
    import json

    return Response(
        content=json.dumps(jsonable_encoder(payload)),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=evalio-export.json",
            "Cache-Control": "private, no-store",
        },
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    session: SessionDependency,
    user: CurrentUserDependency,
    confirm: Annotated[str, Body(embed=True, min_length=6, max_length=20)],
) -> None:
    if confirm != "DELETE":
        raise DomainError("Type DELETE to confirm account deletion", code="INVALID_INPUT")
    await session.execute(delete(User).where(User.id == user.id))
    await session.commit()
