import uuid

import pytest

from api.admission_engine.auth.ownership import require_owner
from api.admission_engine.errors import ForbiddenError


def test_owner_is_allowed() -> None:
    user_id = uuid.uuid4()
    require_owner(resource_user_id=user_id, current_user_id=user_id)


def test_cross_user_access_is_denied() -> None:
    with pytest.raises(ForbiddenError):
        require_owner(resource_user_id=uuid.uuid4(), current_user_id=uuid.uuid4())
