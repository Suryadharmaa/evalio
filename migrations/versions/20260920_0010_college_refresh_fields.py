"""Add fields required by the September college-data refresh.

Revision ID: 20260920_0010
Revises: 20260920_0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260920_0010"
down_revision: str | None = "20260920_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("college_admissions", sa.Column("international_applicants", sa.Integer()))
    op.add_column("college_admissions", sa.Column("international_admits", sa.Integer()))
    op.add_column(
        "college_financial_aid", sa.Column("css_profile_required", sa.Boolean())
    )
    op.add_column(
        "college_financial_aid", sa.Column("books_personal", sa.Numeric(14, 2))
    )


def downgrade() -> None:
    op.drop_column("college_financial_aid", "books_personal")
    op.drop_column("college_financial_aid", "css_profile_required")
    op.drop_column("college_admissions", "international_admits")
    op.drop_column("college_admissions", "international_applicants")
