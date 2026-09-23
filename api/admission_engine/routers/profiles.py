import uuid

from fastapi import APIRouter, Depends, Request, status
from pydantic import ValidationError

from api.admission_engine.application.dependencies import (
    CurrentUserDependency,
    SessionDependency,
    get_identity,
)
from api.admission_engine.config import ENGINE_VERSION
from api.admission_engine.errors import DomainError, NotFoundError
from api.admission_engine.repositories.profiles import ProfileRepository
from api.admission_engine.schemas.profiles import (
    ProfileCreate,
    ProfileFields,
    ProfileRead,
    ProfileUpdate,
)

router = APIRouter(
    prefix="/api/v1/profiles", tags=["profiles"], dependencies=[Depends(get_identity)]
)
me_router = APIRouter(prefix="/api/v1", tags=["profiles"], dependencies=[Depends(get_identity)])


def envelope(request: Request, data: object) -> dict[str, object]:
    return {
        "data": data,
        "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
    }


@me_router.get("/me")
async def get_me(request: Request, user: CurrentUserDependency) -> dict[str, object]:
    return envelope(
        request,
        {"id": user.id, "email": user.email_snapshot, "created_at": user.created_at},
    )


@router.get("")
async def list_profiles(
    request: Request, session: SessionDependency, user: CurrentUserDependency
) -> dict[str, object]:
    profiles = await ProfileRepository(session).list_for_owner(user.id)
    return envelope(request, [ProfileRead.model_validate(profile) for profile in profiles])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: ProfileCreate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    profile = await ProfileRepository(session).create(user.id, payload)
    await session.commit()
    return envelope(request, ProfileRead.model_validate(profile))


@router.get("/{profile_id}")
async def get_profile(
    profile_id: uuid.UUID,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    profile = await ProfileRepository(session).get_for_owner(profile_id, user.id)
    if profile is None:
        raise NotFoundError("Profile not found")
    return envelope(request, ProfileRead.model_validate(profile))


@router.patch("/{profile_id}")
async def update_profile(
    profile_id: uuid.UUID,
    payload: ProfileUpdate,
    request: Request,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> dict[str, object]:
    repository = ProfileRepository(session)
    profile = await repository.get_for_owner(profile_id, user.id)
    if profile is None:
        raise NotFoundError("Profile not found")
    current = ProfileFields.model_validate(profile).model_dump()
    try:
        ProfileFields.model_validate({**current, **payload.model_dump(exclude_unset=True)})
    except ValidationError as error:
        raise DomainError("Profile update is invalid", code="INVALID_INPUT") from error
    profile = await repository.update(profile, payload)
    await session.commit()
    return envelope(request, ProfileRead.model_validate(profile))


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: uuid.UUID,
    session: SessionDependency,
    user: CurrentUserDependency,
) -> None:
    repository = ProfileRepository(session)
    profile = await repository.get_for_owner(profile_id, user.id)
    if profile is None:
        raise NotFoundError("Profile not found")
    await repository.delete(profile)
    await session.commit()
