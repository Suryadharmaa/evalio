"""Send a synthetic essay to the configured provider without printing credentials or prose."""

import asyncio
import json
from typing import Any
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pydantic import ValidationError

from api.admission_engine.application import essay_review
from api.admission_engine.config import get_settings
from api.admission_engine.engine.essay_review import local_analysis
from api.admission_engine.schemas.essay_review import SemanticReview

ESSAY = (
    "I noticed our library door would not close after school. I asked the librarian "
    "how students used the room and learned it stayed open for evening study. We "
    "measured the hinge, sketched a repair, and tested a bracket with three classmates. "
    "The first attempt failed, so I returned with a smaller part and listened to "
    "their ideas. When the door finally closed, I understood that useful work starts "
    "by asking people what they need. I now bring that habit to every project."
)


async def main() -> None:
    settings = get_settings()
    provider = settings.ESSAY_AI_PROVIDER
    key = getattr(settings, f"{provider.upper()}_API_KEY")
    if key is None or not key.get_secret_value().strip():
        print(f"{provider}: API key is not configured")
        return
    model = settings.ESSAY_AI_MODEL or essay_review._DEFAULT_MODELS[provider]
    captured: list[bytes] = []

    class RecordingResponse:
        def __init__(self, response: Any) -> None:
            self.response = response

        def __enter__(self) -> "RecordingResponse":
            self.response.__enter__()
            return self

        def __exit__(self, *args: object) -> None:
            self.response.__exit__(*args)

        def read(self, size: int = -1) -> bytes:
            body: bytes = self.response.read(size)
            captured.append(body)
            return body

    def observing_urlopen(request: Request, *, timeout: int) -> RecordingResponse:
        return RecordingResponse(urlopen(request, timeout=timeout))

    try:
        with patch.object(essay_review, "urlopen", observing_urlopen):
            result = await asyncio.to_thread(
                essay_review._provider_request,
                essay=ESSAY,
                metrics=local_analysis(ESSAY),
                model=model,
                api_key=key.get_secret_value(),
                provider=provider,
                deep=False,
            )
        review = SemanticReview.model_validate(result)
        print(f"{provider}: valid review, score={review.validated_score()}")
    except HTTPError as error:
        print(f"{provider}: HTTP {error.code}")
        try:
            payload = json.load(error)
            detail = payload.get("error", {})
            if isinstance(detail, dict):
                print("error code:", detail.get("code", "unknown"))
                print("error message:", str(detail.get("message", "unknown")).replace(key.get_secret_value(), "[REDACTED]")[:300])
        except (ValueError, OSError):
            pass
    except (OSError, ValueError, ValidationError, KeyError) as error:
        print(f"{provider}: {type(error).__name__}: {str(error)[:300]}")
        if captured:
            try:
                payload = json.loads(b"".join(captured))
                choice = payload.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content")
                print("finish_reason:", choice.get("finish_reason"))
                print("content_start:", repr(content[:180]) if isinstance(content, str) else type(content).__name__)
            except (ValueError, TypeError, KeyError):
                print("response_json=invalid")


if __name__ == "__main__":
    asyncio.run(main())
