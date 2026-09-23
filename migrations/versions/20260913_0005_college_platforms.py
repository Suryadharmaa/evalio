"""Add city and application platform metadata to colleges.

Revision ID: 20260913_0005
Revises: 20260913_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260913_0005"
down_revision: str | None = "20260913_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("colleges", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column(
        "colleges",
        sa.Column("application_platform_primary", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "colleges",
        sa.Column(
            "application_platforms",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_colleges_application_platforms",
        "colleges",
        ["application_platforms"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_colleges_application_platforms", table_name="colleges")
    op.drop_column("colleges", "application_platforms")
    op.drop_column("colleges", "application_platform_primary")
    op.drop_column("colleges", "city")
