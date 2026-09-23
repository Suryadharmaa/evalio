import uuid
from types import SimpleNamespace

import pytest

from api.admission_engine.database.models import User
from api.admission_engine.errors import ForbiddenError
from api.admission_engine.routers import admin


def test_normal_user_cannot_forge_admin_access(monkeypatch: pytest.MonkeyPatch) -> None:
    user = User(id=uuid.uuid4(), auth_subject="normal-user")
    monkeypatch.setattr(admin, "get_settings", lambda: SimpleNamespace(admin_user_ids=frozenset()))
    with pytest.raises(ForbiddenError):
        admin.ensure_admin(user)


def test_configured_auth_subject_is_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    user = User(id=uuid.uuid4(), auth_subject="trusted-admin")
    monkeypatch.setattr(
        admin, "get_settings", lambda: SimpleNamespace(admin_user_ids=frozenset({"trusted-admin"}))
    )
    admin.ensure_admin(user)
