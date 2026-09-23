"""Add persisted essay metrics.

Revision ID: 20260913_0003
Revises: 20260910_0002
"""

from collections.abc import Sequence

from alembic import op

from api.admission_engine.database import models as _models  # noqa: F401
from api.admission_engine.database.base import Base

revision: str = "20260913_0003"
down_revision: str | None = "20260910_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    Base.metadata.tables["essay_metrics"].create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    Base.metadata.tables["essay_metrics"].drop(op.get_bind(), checkfirst=True)
