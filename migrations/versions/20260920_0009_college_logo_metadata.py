"""Add college logo metadata and per-type primary media.

Revision ID: 20260920_0009
Revises: 20260914_0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260920_0009"
down_revision: str | None = "20260914_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("college_media", sa.Column("sha256", sa.String(length=64), nullable=True))
    op.add_column("college_media", sa.Column("content_type", sa.String(length=100), nullable=True))
    op.add_column(
        "college_media", sa.Column("verification_quality", sa.String(length=40), nullable=True)
    )
    op.add_column("college_media", sa.Column("trademark_notice", sa.Boolean(), nullable=True))
    op.drop_index("uq_college_media_primary", table_name="college_media")
    op.create_index(
        "uq_college_media_primary_type",
        "college_media",
        ["college_id", "media_type"],
        unique=True,
        postgresql_where=sa.text("is_primary"),
    )


def downgrade() -> None:
    op.drop_index("uq_college_media_primary_type", table_name="college_media")
    op.create_index(
        "uq_college_media_primary",
        "college_media",
        ["college_id"],
        unique=True,
        postgresql_where=sa.text("is_primary"),
    )
    op.drop_column("college_media", "trademark_notice")
    op.drop_column("college_media", "verification_quality")
    op.drop_column("college_media", "content_type")
    op.drop_column("college_media", "sha256")
