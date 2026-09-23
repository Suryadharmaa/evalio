import hashlib
import hmac
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from api.admission_engine.database.models import RateLimitBucket
from api.admission_engine.database.session import get_session_factory


@dataclass(slots=True)
class Bucket:
    window_start: int
    count: int


class FixedWindowRateLimiter:
    """Per-instance fallback limiter; production may replace storage with PostgreSQL."""

    def __init__(self, salt: str) -> None:
        self._salt = salt.encode()
        self._buckets: dict[tuple[str, str], Bucket] = {}
        self._lock = threading.Lock()

    def subject_hash(self, value: str) -> str:
        return hmac.new(self._salt, value.encode(), hashlib.sha256).hexdigest()

    def allow(self, *, subject: str, route: str, limit: int, window_seconds: int = 3_600) -> bool:
        now = int(time.time())
        window = now - now % window_seconds
        key = (self.subject_hash(subject), route)
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None or bucket.window_start != window:
                self._buckets[key] = Bucket(window_start=window, count=1)
                return True
            if bucket.count >= limit:
                return False
            bucket.count += 1
            return True


class DatabaseRateLimiter:
    """Atomic PostgreSQL limiter shared by all production instances."""

    def __init__(self, salt: str) -> None:
        self._fallback = FixedWindowRateLimiter(salt)

    async def allow(
        self, *, subject: str, route: str, limit: int, window_seconds: int = 3_600
    ) -> bool:
        now = datetime.now(UTC)
        epoch = int(now.timestamp())
        window = datetime.fromtimestamp(epoch - epoch % window_seconds, UTC)
        statement = (
            insert(RateLimitBucket)
            .values(
                subject_hash=self._fallback.subject_hash(subject),
                route_key=route,
                window_start=window,
                request_count=1,
                expires_at=window + timedelta(seconds=window_seconds * 2),
            )
            .on_conflict_do_update(
                index_elements=["subject_hash", "route_key", "window_start"],
                set_={"request_count": RateLimitBucket.request_count + 1},
            )
            .returning(RateLimitBucket.request_count)
        )
        async with get_session_factory()() as session:
            count = await session.scalar(statement)
            await session.execute(delete(RateLimitBucket).where(RateLimitBucket.expires_at < now))
            await session.commit()
        return count is not None and count <= limit
