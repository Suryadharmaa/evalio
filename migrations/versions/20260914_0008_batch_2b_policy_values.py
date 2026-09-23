"""Support Batch 2B nuanced test policies and fee provenance.

Revision ID: 20260914_0008
Revises: 20260914_0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260914_0008"
down_revision: str | None = "20260914_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "college_admissions",
        "test_policy",
        existing_type=sa.String(length=24),
        type_=sa.String(length=48),
        existing_nullable=False,
    )
    op.add_column(
        "college_admissions", sa.Column("application_fee_status", sa.String(length=80))
    )


def downgrade() -> None:
    op.drop_column("college_admissions", "application_fee_status")
    op.alter_column(
        "college_admissions",
        "test_policy",
        existing_type=sa.String(length=48),
        type_=sa.String(length=24),
        existing_nullable=False,
    )
