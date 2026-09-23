"""Add normalized college research and enrichment fields.

Revision ID: 20260914_0007
Revises: 20260914_0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260914_0007"
down_revision: str | None = "20260914_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("colleges", sa.Column("official_name", sa.String(length=240)))
    op.add_column("colleges", sa.Column("selection_group", sa.String(length=80)))
    op.add_column("colleges", sa.Column("identity_confidence", sa.String(length=24)))
    op.create_unique_constraint("uq_colleges_ipeds_id", "colleges", ["ipeds_id"])

    op.add_column("college_admissions", sa.Column("source_cycle", sa.String(length=80)))
    op.add_column("college_admissions", sa.Column("yield_rate_pct", sa.Numeric(7, 3)))
    op.add_column("college_admissions", sa.Column("test_policy_status", sa.String(length=80)))
    op.add_column(
        "college_admissions", sa.Column("application_fee_usd", sa.Numeric(10, 2))
    )
    op.add_column(
        "college_admissions",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.add_column(
        "college_admissions",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_unique_constraint(
        "uq_college_requirements_cycle_type",
        "college_requirements",
        ["college_id", "academic_cycle", "requirement_type"],
    )

    op.add_column("college_financial_aid", sa.Column("source_cycle", sa.String(length=80)))
    op.alter_column(
        "college_financial_aid",
        "need_policy",
        existing_type=sa.String(length=32),
        type_=sa.String(length=48),
        existing_nullable=False,
    )
    op.add_column("college_financial_aid", sa.Column("aid_policy_status", sa.String(length=80)))
    op.add_column(
        "college_financial_aid",
        sa.Column("international_need_based_aid_status", sa.String(length=40)),
    )
    op.add_column(
        "college_financial_aid",
        sa.Column("meets_full_demonstrated_need_status", sa.String(length=64)),
    )
    op.add_column("college_financial_aid", sa.Column("mandatory_fees", sa.Numeric(14, 2)))
    op.add_column("college_financial_aid", sa.Column("cost_basis", sa.String(length=80)))
    op.add_column("college_financial_aid", sa.Column("aid_forms_or_process", sa.Text()))
    op.add_column(
        "college_financial_aid",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.add_column(
        "college_financial_aid",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.alter_column(
        "college_sources",
        "academic_cycle",
        existing_type=sa.String(length=20),
        type_=sa.String(length=80),
        existing_nullable=True,
    )
    op.create_unique_constraint(
        "uq_college_sources_identity",
        "college_sources",
        ["college_id", "field_group", "field_name", "source_url", "academic_cycle"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_college_sources_identity", "college_sources", type_="unique")
    op.alter_column(
        "college_sources",
        "academic_cycle",
        existing_type=sa.String(length=80),
        type_=sa.String(length=20),
        existing_nullable=True,
    )
    op.drop_column("college_financial_aid", "aid_forms_or_process")
    op.drop_column("college_financial_aid", "updated_at")
    op.drop_column("college_financial_aid", "created_at")
    op.drop_column("college_financial_aid", "cost_basis")
    op.drop_column("college_financial_aid", "mandatory_fees")
    op.drop_column("college_financial_aid", "meets_full_demonstrated_need_status")
    op.drop_column("college_financial_aid", "international_need_based_aid_status")
    op.drop_column("college_financial_aid", "aid_policy_status")
    op.drop_column("college_financial_aid", "source_cycle")
    op.alter_column(
        "college_financial_aid",
        "need_policy",
        existing_type=sa.String(length=48),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
    op.drop_constraint(
        "uq_college_requirements_cycle_type", "college_requirements", type_="unique"
    )
    op.drop_column("college_admissions", "application_fee_usd")
    op.drop_column("college_admissions", "updated_at")
    op.drop_column("college_admissions", "created_at")
    op.drop_column("college_admissions", "yield_rate_pct")
    op.drop_column("college_admissions", "test_policy_status")
    op.drop_column("college_admissions", "source_cycle")
    op.drop_constraint("uq_colleges_ipeds_id", "colleges", type_="unique")
    op.drop_column("colleges", "identity_confidence")
    op.drop_column("colleges", "selection_group")
    op.drop_column("colleges", "official_name")
