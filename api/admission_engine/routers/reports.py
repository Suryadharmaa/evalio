import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select

from api.admission_engine.application.dependencies import (
    CurrentUserDependency,
    SessionDependency,
    get_identity,
)
from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.database.models import ApplicantProfile, SavedReport
from api.admission_engine.errors import DomainError, NotFoundError
from api.admission_engine.schemas.reports import (
    ReportRequest,
    SavedReportCreate,
    SavedReportRead,
    StructuredReport,
)

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
profile_reports_router = APIRouter(
    prefix="/api/v1/profiles", tags=["reports"], dependencies=[Depends(get_identity)]
)


def _contains_raw_text(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            key.casefold() in {"raw_text", "essay_text", "lor_text", "recommendation_text"}
            or _contains_raw_text(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_raw_text(item) for item in value)
    return False


@router.post("/preview")
def preview_report(payload: ReportRequest, request: Request) -> dict[str, object]:
    report = StructuredReport(
        report_type=payload.report_type,
        profile_id=payload.profile_id,
        sections=payload.sections,
        generated_at=datetime.now(UTC),
    )
    return {
        "data": {"report": report},
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@profile_reports_router.post("/{profile_id}/reports", status_code=status.HTTP_201_CREATED)
async def create_saved_report(
    profile_id: uuid.UUID,
    payload: SavedReportCreate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    profile = await session.scalar(
        select(ApplicantProfile).where(
            ApplicantProfile.id == profile_id, ApplicantProfile.user_id == user.id
        )
    )
    if profile is None:
        raise NotFoundError("Profile not found")
    sections = payload.sections.model_dump(mode="json")
    if _contains_raw_text(sections):
        raise DomainError(
            "Reports cannot contain raw essay or recommendation text", code="INVALID_INPUT"
        )
    report = StructuredReport(
        report_type=payload.report_type,
        profile_id=str(profile_id),
        sections=sections,
        generated_at=datetime.now(UTC),
    )
    row = SavedReport(
        user_id=user.id,
        profile_id=profile_id,
        report_type=payload.report_type,
        report_version=report.report_version,
        report_json=report.model_dump(mode="json"),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {
        "data": SavedReportRead.model_validate(row),
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@profile_reports_router.get("/{profile_id}/reports")
async def list_saved_reports(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    profile = await session.scalar(
        select(ApplicantProfile).where(
            ApplicantProfile.id == profile_id, ApplicantProfile.user_id == user.id
        )
    )
    if profile is None:
        raise NotFoundError("Profile not found")
    rows = list(
        await session.scalars(
            select(SavedReport)
            .where(SavedReport.profile_id == profile_id, SavedReport.user_id == user.id)
            .order_by(SavedReport.created_at.desc())
            .limit(100)
        )
    )
    return {
        "data": [SavedReportRead.model_validate(row) for row in rows],
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


async def _owned_report(
    report_id: uuid.UUID, session: SessionDependency, user: CurrentUserDependency
) -> SavedReport:
    row = await session.scalar(
        select(SavedReport).where(SavedReport.id == report_id, SavedReport.user_id == user.id)
    )
    if row is None:
        raise NotFoundError("Report not found")
    return row


@router.get("/{report_id}", dependencies=[Depends(get_identity)])
async def get_saved_report(
    report_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    row = await _owned_report(report_id, session, user)
    return {
        "data": SavedReportRead.model_validate(row),
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@router.delete(
    "/{report_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_identity)]
)
async def delete_saved_report(
    report_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    await session.delete(await _owned_report(report_id, session, user))
    await session.commit()
