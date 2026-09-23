from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.admission_engine.auth import AuthIdentity
from api.admission_engine.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(self, identity: AuthIdentity) -> User:
        user = await self._session.scalar(
            select(User).where(User.auth_subject == identity.subject, User.deleted_at.is_(None))
        )
        if user is None:
            user = User(auth_subject=identity.subject, email_snapshot=identity.email)
            self._session.add(user)
            await self._session.flush()
        return user
