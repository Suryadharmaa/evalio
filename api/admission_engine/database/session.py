from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.admission_engine.config import get_settings


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    if settings.DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL is required for persistent operations")
    engine = create_async_engine(
        normalize_database_url(settings.DATABASE_URL.get_secret_value()),
        pool_pre_ping=True,
        pool_recycle=300,
    )
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    factory = get_session_factory()
    async with factory() as session:
        yield session
