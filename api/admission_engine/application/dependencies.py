from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.admission_engine.auth import AuthIdentity, SupabaseTokenVerifier
from api.admission_engine.config import get_settings
from api.admission_engine.database.models import User
from api.admission_engine.database.session import get_db_session
from api.admission_engine.errors import UnauthorizedError
from api.admission_engine.repositories.users import UserRepository

bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_token_verifier() -> SupabaseTokenVerifier:
    return SupabaseTokenVerifier(get_settings())


def get_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> AuthIdentity:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication required")
    return get_token_verifier().verify(credentials.credentials)


async def get_current_user(
    identity: Annotated[AuthIdentity, Depends(get_identity)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    user = await UserRepository(session).get_or_create(identity)
    await session.commit()
    return user


SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
