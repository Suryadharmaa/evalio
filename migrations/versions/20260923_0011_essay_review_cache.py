"""Cache structured essay reviews without storing raw essays.

Revision ID: 20260923_0011
Revises: 20260920_0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "20260923_0011"
down_revision: str | None = "20260920_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "essay_review_cache",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("essay_hash", sa.String(64), nullable=False),
        sa.Column("rubric_version", sa.String(40), nullable=False),
        sa.Column("analysis_version", sa.String(40), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("result_json", JSONB(), nullable=False),
        sa.Column("local_metrics", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "essay_hash", "rubric_version", "analysis_version", "model_version",
            name="uq_essay_review_cache_versioned_hash",
        ),
    )
    op.create_index("ix_essay_review_cache_essay_hash", "essay_review_cache", ["essay_hash"])


def downgrade() -> None:
    op.drop_index("ix_essay_review_cache_essay_hash", table_name="essay_review_cache")
    op.drop_table("essay_review_cache")
