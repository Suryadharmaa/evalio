from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, cast

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from api.admission_engine.auth.verifier import SupabaseTokenVerifier
from api.admission_engine.errors import UnauthorizedError


class StaticKeyClient:
    def __init__(self, key: object) -> None:
        self.key = key

    def get_signing_key_from_jwt(self, token: str) -> Any:
        return SimpleNamespace(key=self.key)


def verifier_and_key() -> tuple[SupabaseTokenVerifier, object]:
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = object.__new__(SupabaseTokenVerifier)
    target = cast(Any, verifier)
    target._issuer = "https://example.supabase.co/auth/v1"
    target._audience = "authenticated"
    target._jwks_client = StaticKeyClient(private.public_key())
    return verifier, private


def token(private: object, **overrides: object) -> str:
    now = datetime.now(UTC)
    claims: dict[str, object] = {
        "sub": "user-123",
        "email": "user@example.com",
        "aud": "authenticated",
        "iss": "https://example.supabase.co/auth/v1",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        **overrides,
    }
    return jwt.encode(claims, private, algorithm="RS256")  # type: ignore[arg-type]


def test_valid_token_is_verified() -> None:
    verifier, private = verifier_and_key()
    identity = verifier.verify(token(private))
    assert identity.subject == "user-123"


@pytest.mark.parametrize(
    "encoded",
    [
        lambda key: "malformed",
        lambda key: token(key, exp=datetime.now(UTC) - timedelta(seconds=1)),
        lambda key: token(key, iss="https://attacker.example/auth/v1"),
        lambda key: token(key, aud="wrong"),
    ],
)
def test_invalid_tokens_are_rejected(encoded: Any) -> None:
    verifier, private = verifier_and_key()
    with pytest.raises(UnauthorizedError):
        verifier.verify(encoded(private))
