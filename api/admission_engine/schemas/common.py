from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, allow_inf_nan=False)


class ResponseMeta(ApiModel):
    request_id: str
    engine_version: str | None = None


class SuccessEnvelope(ApiModel):
    data: Any
    meta: ResponseMeta


class ErrorBody(ApiModel):
    code: str
    message: str
    fields: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(ApiModel):
    error: ErrorBody
    meta: ResponseMeta
