from typing import Literal

from pydantic import ConfigDict

from api.admission_engine.schemas.common import ApiModel


class HealthResponse(ApiModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    engine_version: str
