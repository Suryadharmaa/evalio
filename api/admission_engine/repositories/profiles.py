import uuid
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.admission_engine.database.models import ApplicantProfile
from api.admission_engine.schemas.profiles import ProfileCreate, ProfileUpdate


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_owner(self, user_id: uuid.UUID) -> list[ApplicantProfile]:
        result = await self._session.scalars(
            select(ApplicantProfile)
            .where(ApplicantProfile.user_id == user_id)
            .order_by(ApplicantProfile.created_at, ApplicantProfile.id)
        )
        return list(result)

    async def get_for_owner(
        self, profile_id: uuid.UUID, user_id: uuid.UUID
    ) -> ApplicantProfile | None:
        return cast(
            ApplicantProfile | None,
            await self._session.scalar(
                select(ApplicantProfile).where(
                    ApplicantProfile.id == profile_id,
                    ApplicantProfile.user_id == user_id,
                )
            ),
        )

    async def create(self, user_id: uuid.UUID, payload: ProfileCreate) -> ApplicantProfile:
        profile = ApplicantProfile(user_id=user_id, **payload.model_dump())
        self._session.add(profile)
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def update(self, profile: ApplicantProfile, payload: ProfileUpdate) -> ApplicantProfile:
        for name, value in payload.model_dump(exclude_unset=True).items():
            setattr(profile, name, value)
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def delete(self, profile: ApplicantProfile) -> None:
        await self._session.delete(profile)
        await self._session.flush()
