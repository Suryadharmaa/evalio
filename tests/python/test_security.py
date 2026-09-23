import pytest

from api.admission_engine.application.factory import create_app
from api.admission_engine.config import get_settings
from api.admission_engine.security.rate_limit import FixedWindowRateLimiter


def test_fixed_window_limit_and_subject_hashing() -> None:
    limiter = FixedWindowRateLimiter("secret-salt")
    assert limiter.allow(subject="127.0.0.1", route="essay", limit=2)
    assert limiter.allow(subject="127.0.0.1", route="essay", limit=2)
    assert not limiter.allow(subject="127.0.0.1", route="essay", limit=2)
    assert limiter.subject_hash("127.0.0.1") != "127.0.0.1"


def test_production_refuses_missing_security_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("IP_HASH_SALT", raising=False)
    get_settings.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="IP_HASH_SALT"):
            create_app()
    finally:
        get_settings.cache_clear()


def test_production_rejects_wildcard_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql+psycopg://user:pass@db.example.com/evalio",
        "SUPABASE_URL": "https://project.supabase.co",
        "SUPABASE_JWKS_URL": "https://project.supabase.co/auth/v1/.well-known/jwks.json",
        "IP_HASH_SALT": "test-salt",
        "ALLOWED_HOSTS": "evalio.example.com",
        "ALLOWED_ORIGINS": "*",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="exact HTTPS origins"):
            create_app()
    finally:
        get_settings.cache_clear()
