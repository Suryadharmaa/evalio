"""Add licensed college media records.

Revision ID: 20260914_0006
Revises: 20260913_0005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260914_0006"
down_revision: str | None = "20260913_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "college_media",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("media_type", sa.String(length=24), nullable=False),
        sa.Column("image_url", sa.String(length=1_000), nullable=False),
        sa.Column("source_url", sa.String(length=1_000), nullable=False),
        sa.Column("license", sa.String(length=80), nullable=False),
        sa.Column("attribution", sa.String(length=500), nullable=True),
        sa.Column("alt_text", sa.String(length=300), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["college_id"], ["colleges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("college_id", "image_url"),
    )
    op.create_index(
        "uq_college_media_primary",
        "college_media",
        ["college_id"],
        unique=True,
        postgresql_where=sa.text("is_primary"),
    )


def downgrade() -> None:
    op.drop_index("uq_college_media_primary", table_name="college_media")
    op.drop_table("college_media")
