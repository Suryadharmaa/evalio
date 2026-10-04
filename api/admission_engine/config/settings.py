import os
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: SecretStr | None = None
    SUPABASE_URL: str | None = None
    SUPABASE_SECRET_KEY: SecretStr | None = None
    SUPABASE_JWKS_URL: str | None = None
    SUPABASE_JWT_AUDIENCE: str = "authenticated"
    ADMIN_USER_IDS: str = ""
    IP_HASH_SALT: SecretStr | None = None
    ALLOWED_HOSTS: str = ""
    ALLOWED_ORIGINS: str = ""
    SCORING_ENGINE_VERSION: Literal["v1", "v2"] = "v1"
    ESSAY_AI_PROVIDER: Literal["groq", "routeway", "gemini"] = "gemini"
    GROQ_API_KEY: SecretStr | None = None
    ROUTEWAY_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None
    ESSAY_AI_MODEL: str | None = None

    @property
    def allowed_origins(self) -> list[str]:
        configured = [value.strip() for value in self.ALLOWED_ORIGINS.split(",") if value.strip()]
        return configured or ["http://localhost:3000"]

    @property
    def admin_user_ids(self) -> frozenset[str]:
        return frozenset(value.strip() for value in self.ADMIN_USER_IDS.split(",") if value.strip())

    @property
    def allowed_hosts(self) -> list[str]:
        configured = [value.strip() for value in self.ALLOWED_HOSTS.split(",") if value.strip()]
        if configured:
            return configured
        return ["localhost", "127.0.0.1", "testserver"]


@lru_cache
def get_settings() -> Settings:
    if os.environ.get("EVALIO_DISABLE_DOTENV") == "1":
        return Settings(_env_file=None)  # type: ignore[call-arg]
    return Settings(_env_file=(".env", ".env.local"))  # type: ignore[call-arg]
