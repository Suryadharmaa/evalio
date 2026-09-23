import uuid
from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.admission_engine.database.models import (
    College,
    CollegeAdmissions,
    CollegeCdsFactor,
    CollegeFinancialAid,
    CollegeMedia,
    CollegeRequirement,
    CollegeSource,
)
from api.admission_engine.schemas.colleges import CollegeListParams


@dataclass(frozen=True)
class CollegeListRecord:
    college: College
    test_policy: str | None
    need_policy: str | None
    primary_media: CollegeMedia | None


class CollegeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _filtered(self, params: CollegeListParams) -> Select[tuple[College]]:
        query = select(College).where(College.active.is_(True))
        if params.q:
            query = query.where(College.normalized_name.contains(params.q.strip().casefold()))
        query = query.where(College.country_code == params.country.upper())
        if params.state:
            query = query.where(func.upper(College.state_region) == params.state.upper())
        if params.test_policy:
            latest_admission_cycle = (
                select(func.max(CollegeAdmissions.academic_cycle))
                .where(CollegeAdmissions.college_id == College.id)
                .correlate(College)
                .scalar_subquery()
            )
            query = query.join(CollegeAdmissions).where(
                CollegeAdmissions.academic_cycle == latest_admission_cycle
            )
            query = query.where(CollegeAdmissions.test_policy == params.test_policy)
        if params.selectivity_band:
            latest_acceptance_rate = (
                select(CollegeAdmissions.acceptance_rate)
                .where(CollegeAdmissions.college_id == College.id)
                .order_by(CollegeAdmissions.academic_cycle.desc())
                .limit(1)
                .correlate(College)
                .scalar_subquery()
            )
            if params.selectivity_band == "UNDER_10":
                query = query.where(latest_acceptance_rate < 0.10)
            elif params.selectivity_band == "10_TO_20":
                query = query.where(latest_acceptance_rate >= 0.10, latest_acceptance_rate < 0.20)
            elif params.selectivity_band == "20_TO_40":
                query = query.where(latest_acceptance_rate >= 0.20, latest_acceptance_rate < 0.40)
            elif params.selectivity_band == "OVER_40":
                query = query.where(latest_acceptance_rate >= 0.40)
            elif params.selectivity_band == "UNKNOWN":
                query = query.where(latest_acceptance_rate.is_(None))
        if params.need_policy:
            latest_financial_cycle = (
                select(func.max(CollegeFinancialAid.academic_cycle))
                .where(CollegeFinancialAid.college_id == College.id)
                .correlate(College)
                .scalar_subquery()
            )
            query = query.join(CollegeFinancialAid).where(
                CollegeFinancialAid.academic_cycle == latest_financial_cycle,
                CollegeFinancialAid.need_policy == params.need_policy,
            )
        if params.application_platform:
            query = query.where(
                College.application_platforms.contains([params.application_platform])
            )
        if params.institution_type:
            query = query.where(College.institution_type == params.institution_type)
        return query.distinct()

    async def list_colleges(self, params: CollegeListParams) -> tuple[list[CollegeListRecord], int]:
        filtered = self._filtered(params)
        total = (
            await self._session.scalar(select(func.count()).select_from(filtered.subquery())) or 0
        )
        colleges = list(await self._session.scalars(self._paginated(filtered, params)))
        if not colleges:
            return [], total
        ids = [college.id for college in colleges]
        admissions = list(await self._session.scalars(select(CollegeAdmissions).where(CollegeAdmissions.college_id.in_(ids)).order_by(CollegeAdmissions.college_id, CollegeAdmissions.academic_cycle.desc())))
        aid_rows = list(await self._session.scalars(select(CollegeFinancialAid).where(CollegeFinancialAid.college_id.in_(ids)).order_by(CollegeFinancialAid.college_id, CollegeFinancialAid.academic_cycle.desc())))
        media_rows = list(
            await self._session.scalars(
                select(CollegeMedia)
                .where(
                    CollegeMedia.college_id.in_(ids),
                    CollegeMedia.media_type == "LOGO",
                    CollegeMedia.is_primary.is_(True),
                )
                .order_by(CollegeMedia.college_id, CollegeMedia.verified_at.desc())
            )
        )
        latest_admission: dict[uuid.UUID, CollegeAdmissions] = {}
        latest_aid: dict[uuid.UUID, CollegeFinancialAid] = {}
        primary_media: dict[uuid.UUID, CollegeMedia] = {}
        for admission_row in admissions:
            latest_admission.setdefault(admission_row.college_id, admission_row)
        for aid_row in aid_rows:
            latest_aid.setdefault(aid_row.college_id, aid_row)
        for media_row in media_rows:
            primary_media.setdefault(media_row.college_id, media_row)
        records: list[CollegeListRecord] = []
        for college in colleges:
            admission = latest_admission.get(college.id)
            aid = latest_aid.get(college.id)
            records.append(CollegeListRecord(college=college, test_policy=admission.test_policy if admission else None, need_policy=aid.need_policy if aid else None, primary_media=primary_media.get(college.id)))
        return records, total

    @staticmethod
    def _paginated(
        filtered: Select[tuple[College]], params: CollegeListParams
    ) -> Select[tuple[College]]:
        return (
            filtered.order_by(College.name, College.id)
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )

    async def get_by_slug(
        self, slug: str
    ) -> (
        tuple[
            College,
            CollegeAdmissions | None,
            list[CollegeRequirement],
            CollegeFinancialAid | None,
            list[CollegeCdsFactor],
            list[CollegeSource],
            list[CollegeMedia],
        ]
        | None
    ):
        college = await self._session.scalar(
            select(College).where(College.slug == slug, College.active.is_(True))
        )
        if college is None:
            return None
        admission = await self._session.scalar(
            select(CollegeAdmissions)
            .where(CollegeAdmissions.college_id == college.id)
            .order_by(CollegeAdmissions.academic_cycle.desc())
            .limit(1)
        )
        requirement_cycle = await self._session.scalar(
            select(func.max(CollegeRequirement.academic_cycle)).where(
                CollegeRequirement.college_id == college.id
            )
        )
        requirements = (
            list(
                await self._session.scalars(
                    select(CollegeRequirement)
                    .where(
                        CollegeRequirement.college_id == college.id,
                        CollegeRequirement.academic_cycle == requirement_cycle,
                    )
                    .order_by(CollegeRequirement.requirement_type)
                )
            )
            if requirement_cycle is not None
            else []
        )
        financial_aid = await self._session.scalar(
            select(CollegeFinancialAid)
            .where(CollegeFinancialAid.college_id == college.id)
            .order_by(CollegeFinancialAid.academic_cycle.desc())
            .limit(1)
        )
        cds_cycle = await self._session.scalar(
            select(func.max(CollegeCdsFactor.academic_cycle)).where(
                CollegeCdsFactor.college_id == college.id
            )
        )
        cds_factors = (
            list(
                await self._session.scalars(
                    select(CollegeCdsFactor)
                    .where(
                        CollegeCdsFactor.college_id == college.id,
                        CollegeCdsFactor.academic_cycle == cds_cycle,
                    )
                    .order_by(CollegeCdsFactor.factor_name)
                )
            )
            if cds_cycle is not None
            else []
        )
        sources = list(
            await self._session.scalars(
                select(CollegeSource)
                .where(CollegeSource.college_id == college.id)
                .order_by(CollegeSource.field_group, CollegeSource.field_name)
            )
        )
        media = list(
            await self._session.scalars(
                select(CollegeMedia)
                .where(CollegeMedia.college_id == college.id)
                .order_by(CollegeMedia.is_primary.desc(), CollegeMedia.verified_at.desc())
            )
        )
        return college, admission, requirements, financial_aid, cds_factors, sources, media
