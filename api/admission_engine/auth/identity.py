from pydantic import BaseModel, ConfigDict, Field


class AuthIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    subject: str = Field(min_length=1, max_length=128)
    email: str | None = Field(default=None, max_length=320)
    audience: str | tuple[str, ...] | None = None
    issuer: str | None = None
