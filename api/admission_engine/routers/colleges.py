from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from api.admission_engine.application.dependencies import SessionDependency
from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.engine.enums import NeedPolicy, TestPolicy
from api.admission_engine.errors import NotFoundError
from api.admission_engine.repositories.colleges import CollegeRepository
from api.admission_engine.schemas.colleges import (
    AdmissionSnapshot,
    CdsFactorRead,
    CollegeDetail,
    CollegeListParams,
    CollegeSummary,
    FinancialAidRead,
    MediaRead,
    RequirementRead,
    SourceRead,
)

router = APIRouter(prefix="/api/v1/colleges", tags=["colleges"])


@router.get("")
async def list_colleges(
    request: Request,
    session: SessionDependency,
    q: Annotated[str | None, Query(max_length=120)] = None,
    country: Annotated[str, Query(pattern=r"^[A-Za-z]{2}$")] = "US",
    state: Annotated[str | None, Query(max_length=80)] = None,
    test_policy: TestPolicy | None = None,
    need_policy: NeedPolicy | None = None,
    application_platform: Annotated[
        str | None, Query(max_length=40, pattern=r"^[A-Z][A-Z0-9_]*$")
    ] = None,
    institution_type: Annotated[str | None, Query(max_length=80, pattern=r"^[A-Z][A-Z0-9_]*$")] = None,
    selectivity_band: Annotated[str | None, Query(pattern=r"^(UNDER_10|10_TO_20|20_TO_40|OVER_40|UNKNOWN)$")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
) -> dict[str, object]:
    params = CollegeListParams(
        q=q,
        country=country,
        state=state,
        test_policy=test_policy,
        need_policy=need_policy,
        application_platform=application_platform,
        institution_type=institution_type,
        selectivity_band=selectivity_band,
        page=page,
        page_size=page_size,
    )
    colleges, total = await CollegeRepository(session).list_colleges(params)
    return {
        "data": [CollegeSummary(**CollegeSummary.model_validate(item.college).model_dump(exclude={"test_policy", "need_policy", "primary_media"}), test_policy=item.test_policy, need_policy=item.need_policy, primary_media=MediaRead.model_validate(item.primary_media) if item.primary_media else None) for item in colleges],
        "meta": {
            "request_id": request.state.request_id,
            "engine_version": ENGINE_VERSION,
            "page": page,
            "page_size": page_size,
            "total": total,
        },
    }


@router.get("/{slug}")
async def get_college(
    slug: Annotated[str, Path(min_length=1, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")],
    request: Request,
    session: SessionDependency,
) -> dict[str, object]:
    result = await CollegeRepository(session).get_by_slug(slug)
    if result is None:
        raise NotFoundError("College not found")
    college, admission, requirements, financial_aid, cds_factors, sources, media = result
    detail = CollegeDetail(
        **CollegeSummary.model_validate(college).model_dump(exclude={"test_policy", "need_policy", "primary_media"}),
        test_policy=admission.test_policy if admission else None,
        need_policy=financial_aid.need_policy if financial_aid else None,
        primary_media=MediaRead.model_validate(
            next(
                (item for item in media if item.media_type == "LOGO" and item.is_primary),
                media[0],
            )
        )
        if media
        else None,
        common_app_member=college.common_app_member,
        admissions=AdmissionSnapshot.model_validate(admission) if admission else None,
        requirements=[RequirementRead.model_validate(item) for item in requirements],
        financial_aid=FinancialAidRead.model_validate(financial_aid) if financial_aid else None,
        cds_factors=[CdsFactorRead.model_validate(item) for item in cds_factors],
        sources=[SourceRead.model_validate(item) for item in sources],
        media=[MediaRead.model_validate(item) for item in media],
    )
    return {
        "data": detail,
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }
