import json
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import Response

from api.admission_engine.application.dependencies import get_token_verifier
from api.admission_engine.config import (
    ENGINE_VERSION,
    RUBRIC_VERSIONS,
    RULEBOOK_VERSION,
    SCHEMA_REVISION,
    get_settings,
)
from api.admission_engine.database.session import get_db_session
from api.admission_engine.errors import (
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from api.admission_engine.routers.account import router as account_router
from api.admission_engine.routers.admin import router as admin_router
from api.admission_engine.routers.calculators import router as calculators_router
from api.admission_engine.routers.colleges import router as colleges_router
from api.admission_engine.routers.essay_ideas import router as essay_ideas_router
from api.admission_engine.routers.essay_review import router as essay_review_router
from api.admission_engine.routers.evaluations import router as evaluations_router
from api.admission_engine.routers.lor_builder import router as lor_builder_router
from api.admission_engine.routers.profile_data import router as profile_data_router
from api.admission_engine.routers.profiles import me_router
from api.admission_engine.routers.profiles import router as profiles_router
from api.admission_engine.routers.reports import profile_reports_router
from api.admission_engine.routers.reports import router as reports_router
from api.admission_engine.schemas import HealthResponse
from api.admission_engine.security.rate_limit import DatabaseRateLimiter, FixedWindowRateLimiter

logger = logging.getLogger("evalio.api")
RATE_LIMITS = {
    "/api/v1/evaluations/essay": 20,
    "/api/v1/essay-review": 20,
    "/api/v1/essay-review/deep": 10,
    "/api/v1/evaluations/writing-patterns": 20,
    "/api/v1/evaluations/coursework": 30,
    "/api/v1/essay-ideas/build": 20,
    "/api/v1/lor/build": 20,
    "/api/v1/calculators/gpa": 60,
    "/api/v1/evaluations/essay/compare": 20,
    "/api/v1/evaluations/activity-description": 40,
    "/api/v1/colleges": 120,
    "/api/v1/evaluations/college": 30,
    "/api/v1/reports/preview": 10,
}


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.APP_ENV.casefold() == "production":
        missing = [
            name
            for name in (
                "DATABASE_URL",
                "SUPABASE_URL",
                "SUPABASE_JWKS_URL",
                "IP_HASH_SALT",
                "ALLOWED_HOSTS",
                "ALLOWED_ORIGINS",
            )
            if getattr(settings, name) is None
            or (isinstance(getattr(settings, name), str) and not getattr(settings, name).strip())
        ]
        if missing:
            raise RuntimeError(f"Required production settings are missing: {', '.join(missing)}")
        if any("*" in host for host in settings.allowed_hosts):
            raise RuntimeError("Production ALLOWED_HOSTS cannot contain a wildcard")
        invalid_origins = [
            origin
            for origin in settings.allowed_origins
            if origin == "*"
            or (parts := urlsplit(origin)).scheme != "https"
            or not parts.netloc
            or parts.username is not None
            or parts.password is not None
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
        ]
        if invalid_origins:
            raise RuntimeError("Production ALLOWED_ORIGINS must contain exact HTTPS origins")
    salt = (
        settings.IP_HASH_SALT.get_secret_value()
        if settings.IP_HASH_SALT
        else "development-only-salt"
    )
    limiter = (
        DatabaseRateLimiter(salt)
        if settings.APP_ENV.casefold() == "production"
        else FixedWindowRateLimiter(salt)
    )
    app = FastAPI(
        title="Evalio API",
        version=ENGINE_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        route_key = request.url.path
        limit = RATE_LIMITS.get(route_key)
        if route_key == "/api/v1/evaluations/essay/upload":
            limit, route_key = 20, "/api/v1/evaluations/essay"
        elif re.fullmatch(r"/api/v1/profiles/[^/]+/colleges/[^/]+/evaluate", route_key):
            limit, route_key = 30, "/api/v1/profiles/{id}/colleges/{id}/evaluate"
        elif re.fullmatch(r"/api/v1/profiles/[^/]+/reports", route_key) and request.method == "POST":
            limit, route_key = 10, "/api/v1/profiles/{id}/reports"
        client_subject = request.client.host if request.client else "unknown"
        authorization = request.headers.get("authorization")
        authenticated_limit = route_key.startswith("/api/v1/profiles/")
        subject = client_subject
        if authenticated_limit and authorization:
            scheme, _, token = authorization.partition(" ")
            if scheme.casefold() == "bearer" and token:
                with suppress(UnauthorizedError):
                    subject = get_token_verifier().verify(token).subject
        allowed = True
        if limit is not None:
            if isinstance(limiter, DatabaseRateLimiter):
                allowed = await limiter.allow(subject=subject, route=route_key, limit=limit)
            else:
                allowed = limiter.allow(subject=subject, route=route_key, limit=limit)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Request limit reached. Try again later.",
                        "fields": {},
                    },
                    "meta": {"request_id": request_id},
                },
                headers={"x-request-id": request_id, "Cache-Control": "no-store"},
            )
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Frame-Options"] = "DENY"
        if settings.APP_ENV.casefold() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.url.path.startswith(
            (
                "/api/v1/profiles",
                "/api/v1/account",
                "/api/v1/reports",
                "/api/v1/admin",
                "/api/v1/me",
            )
        ):
            response.headers["Cache-Control"] = "private, no-store"
        if request.url.path.startswith(("/api/v1/evaluations", "/api/v1/essay-ideas", "/api/v1/essay-review", "/api/v1/lor", "/api/v1/calculators")):
            response.headers["Cache-Control"] = "no-store"
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "route": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1_000, 2),
                    "engine_version": ENGINE_VERSION,
                }
            )
        )
        return response

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, error: DomainError) -> JSONResponse:
        status_code = 400
        if isinstance(error, UnauthorizedError):
            status_code = 401
        elif isinstance(error, ForbiddenError):
            status_code = 403
        elif isinstance(error, NotFoundError):
            status_code = 404
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {"code": error.code, "message": str(error), "fields": {}},
                "meta": {"request_id": request.state.request_id},
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        fields = {
            ".".join(str(part) for part in item["loc"]): item["msg"] for item in error.errors()
        }
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Request validation failed.",
                    "fields": fields,
                },
                "meta": {"request_id": request.state.request_id},
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        logger.error(
            "Unhandled API error type=%s request_id=%s",
            type(error).__name__,
            getattr(request.state, "request_id", "unknown"),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "fields": {},
                },
                "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
            },
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/v1/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok", engine_version=ENGINE_VERSION)

    @app.get("/api/v1/health/ready", tags=["system"])
    async def readiness(
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> Response:
        try:
            revision = await session.scalar(sql_text("SELECT version_num FROM alembic_version"))
        except Exception:
            revision = None
        ready = revision == SCHEMA_REVISION
        return JSONResponse(
            status_code=200 if ready else 503,
            content={
                "status": "ready" if ready else "not_ready",
                "engine_version": ENGINE_VERSION,
                "schema_revision": revision,
                "expected_schema_revision": SCHEMA_REVISION,
            },
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/v1/methodology", tags=["system"])
    def methodology(request: Request) -> dict[str, object]:
        return {
            "data": {
                "engine_version": ENGINE_VERSION,
                "rulebook_version": RULEBOOK_VERSION,
                "rubric_versions": RUBRIC_VERSIONS,
                "determinism": "same input + same data snapshot + same versions = same result",
                "limitations": [
                    "Scores are internal planning metrics, not official ratings.",
                    "College categories are not acceptance probabilities or guarantees.",
                    "Text analysis measures mechanical signals, not authenticity or emotion.",
                ],
            },
            "meta": {"request_id": request.state.request_id, "engine_version": ENGINE_VERSION},
        }

    app.include_router(account_router)
    app.include_router(admin_router)
    app.include_router(calculators_router)
    app.include_router(colleges_router)
    app.include_router(evaluations_router)
    app.include_router(essay_ideas_router)
    app.include_router(essay_review_router)
    app.include_router(lor_builder_router)
    app.include_router(profiles_router)
    app.include_router(me_router)
    app.include_router(profile_data_router)
    app.include_router(reports_router)
    app.include_router(profile_reports_router)
    return app
