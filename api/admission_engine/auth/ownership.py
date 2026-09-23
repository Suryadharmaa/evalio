import uuid

from api.admission_engine.errors import ForbiddenError


def require_owner(*, resource_user_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
    if resource_user_id != current_user_id:
        raise ForbiddenError("You do not have access to this resource")
