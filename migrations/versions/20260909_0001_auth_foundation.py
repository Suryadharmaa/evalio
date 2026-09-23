"""Create user and applicant profile foundations."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260909_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_subject", sa.String(length=128), nullable=False),
        sa.Column("email_snapshot", sa.String(length=320), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("auth_subject", name="uq_users_auth_subject"),
    )
    op.create_table(
        "applicant_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_name", sa.String(length=120), nullable=False),
        sa.Column("applicant_type", sa.String(length=24), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("curriculum_type", sa.String(length=80), nullable=True),
        sa.Column("grading_scale_name", sa.String(length=80), nullable=True),
        sa.Column("grading_scale_min", sa.Numeric(10, 3), nullable=True),
        sa.Column("grading_scale_max", sa.Numeric(10, 3), nullable=True),
        sa.Column("intended_major", sa.String(length=160), nullable=True),
        sa.Column("school_name", sa.String(length=240), nullable=True),
        sa.Column("class_size", sa.Integer(), nullable=True),
        sa.Column("class_rank", sa.Integer(), nullable=True),
        sa.Column("max_family_contribution", sa.Numeric(14, 2), nullable=True),
        sa.Column("budget_currency", sa.String(length=3), nullable=True),
        sa.Column("requires_need_based_aid", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_applicant_profiles_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_applicant_profiles"),
    )
    op.create_index("ix_applicant_profiles_user_id_id", "applicant_profiles", ["user_id", "id"])


def downgrade() -> None:
    op.drop_index("ix_applicant_profiles_user_id_id", table_name="applicant_profiles")
    op.drop_table("applicant_profiles")
    op.drop_table("users")
