from typing import Any

import jwt
from jwt import PyJWKClient

from api.admission_engine.auth.identity import AuthIdentity
from api.admission_engine.config import Settings
from api.admission_engine.errors import UnauthorizedError


class SupabaseTokenVerifier:
    def __init__(self, settings: Settings) -> None:
        if not settings.SUPABASE_JWKS_URL or not settings.SUPABASE_URL:
            raise RuntimeError("Supabase JWT verification configuration is incomplete")
        self._issuer = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
        self._audience = settings.SUPABASE_JWT_AUDIENCE
        self._jwks_client = PyJWKClient(settings.SUPABASE_JWKS_URL, cache_keys=True)

    def verify(self, token: str) -> AuthIdentity:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "sub"]},
            )
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired access token") from exc

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise UnauthorizedError("Access token subject is missing")
        return AuthIdentity(
            subject=subject,
            email=claims.get("email") if isinstance(claims.get("email"), str) else None,
            audience=claims.get("aud"),
            issuer=claims.get("iss") if isinstance(claims.get("iss"), str) else None,
        )
