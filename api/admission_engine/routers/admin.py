import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from pydantic import Field, model_validator
from sqlalchemy import select

from api.admission_engine.application.dependencies import (
    CurrentUserDependency,
    SessionDependency,
    get_identity,
)
from api.admission_engine.config import ENGINE_VERSION, get_settings
from api.admission_engine.database.models import AdminImportRun, CollegeSource
from api.admission_engine.errors import DomainError, ForbiddenError, NotFoundError
from api.admission_engine.schemas.common import ApiModel

router = APIRouter(prefix="/api/v1/admin", tags=["admin"], dependencies=[Depends(get_identity)])


class ImportCreate(ApiModel):
    import_type: str = Field(min_length=1, max_length=80)
    academic_cycle: str | None = Field(default=None, max_length=20)
    rows_read: int = Field(default=0, ge=0)
    rows_valid: int = Field(default=0, ge=0)
    rows_rejected: int = Field(default=0, ge=0)
    diff_summary: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_diff_summary_size(self) -> "ImportCreate":
        if len(json.dumps(self.diff_summary, default=str).encode()) > 100_000:
            raise ValueError("diff_summary exceeds 100 KB")
        return self


class Confirmation(ApiModel):
    confirm: str = Field(min_length=7, max_length=20)


def ensure_admin(user: CurrentUserDependency) -> None:
    configured = get_settings().admin_user_ids
    if str(user.id) not in configured and user.auth_subject not in configured:
        raise ForbiddenError("Administrator access required")


def envelope(request: Request, data: object) -> dict[str, object]:
    return {
        "data": data,
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


async def get_run(run_id: uuid.UUID, session: SessionDependency) -> AdminImportRun:
    row = await session.get(AdminImportRun, run_id)
    if row is None:
        raise NotFoundError("Import run not found")
    return row


@router.post("/imports", status_code=status.HTTP_201_CREATED)
async def create_import(
    payload: ImportCreate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key", max_length=160)] = None,
) -> dict[str, object]:
    ensure_admin(user)
    if idempotency_key:
        existing = await session.scalar(
            select(AdminImportRun).where(AdminImportRun.idempotency_key == idempotency_key)
        )
        if existing is not None:
            return envelope(request, existing)
    row = AdminImportRun(
        admin_user_id=user.id,
        idempotency_key=idempotency_key,
        status="IMPORTED",
        **payload.model_dump(),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return envelope(request, row)


@router.get("/imports/{run_id}")
async def read_import(
    run_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    ensure_admin(user)
    return envelope(request, await get_run(run_id, session))


@router.post("/imports/{run_id}/validate")
async def validate_import(
    run_id: uuid.UUID, request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    ensure_admin(user)
    row = await get_run(run_id, session)
    if row.status not in {"IMPORTED", "REJECTED"}:
        raise DomainError("Only imported rows can be validated", code="INVALID_STATE")
    row.status = (
        "VALID" if row.rows_rejected == 0 and row.rows_valid == row.rows_read else "REJECTED"
    )
    await session.commit()
    return envelope(request, row)


@router.post("/imports/{run_id}/approve")
async def approve_import(
    run_id: uuid.UUID,
    payload: Confirmation,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    ensure_admin(user)
    row = await get_run(run_id, session)
    if payload.confirm != "APPROVE" or row.status != "VALID":
        raise DomainError(
            "A valid import and explicit APPROVE confirmation are required", code="INVALID_STATE"
        )
    row.status = "APPROVED"
    row.approved_at = datetime.now(UTC)
    await session.commit()
    return envelope(request, row)


@router.post("/imports/{run_id}/promote")
async def promote_import(
    run_id: uuid.UUID,
    payload: Confirmation,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    ensure_admin(user)
    row = await get_run(run_id, session)
    if payload.confirm != "PROMOTE" or row.status != "APPROVED":
        raise DomainError(
            "An approved import and explicit PROMOTE confirmation are required",
            code="INVALID_STATE",
        )
    row.status = "PROMOTED"
    await session.commit()
    return envelope(request, row)


@router.get("/sources/stale")
async def stale_sources(
    request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    ensure_admin(user)
    cutoff = datetime.now(UTC) - timedelta(days=365)
    rows = list(
        await session.scalars(
            select(CollegeSource).where(
                (CollegeSource.verified_at.is_(None)) | (CollegeSource.verified_at < cutoff)
            )
        )
    )
    return envelope(request, rows)


@router.get("/rules")
async def rules(request: Request, user: CurrentUserDependency) -> dict[str, object]:
    ensure_admin(user)
    return envelope(request, {"engine_version": ENGINE_VERSION, "registry": "deterministic"})


@router.get("/system")
async def system(request: Request, user: CurrentUserDependency) -> dict[str, object]:
    ensure_admin(user)
    return envelope(request, {"status": "ok", "environment": get_settings().APP_ENV})
