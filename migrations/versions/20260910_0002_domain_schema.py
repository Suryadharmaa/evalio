"""Add structured applicant, college, evaluation, and reporting tables.

Revision ID: 20260910_0002
Revises: 20260909_0001
"""

from collections.abc import Sequence

from alembic import op

from api.admission_engine.database import models as _models  # noqa: F401
from api.admission_engine.database.base import Base

revision: str = "20260910_0002"
down_revision: str | None = "20260909_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DOMAIN_TABLES = (
    "colleges",
    "college_admissions",
    "college_requirements",
    "college_financial_aid",
    "college_cds_factors",
    "college_sources",
    "admin_import_runs",
    "academic_terms",
    "courses",
    "school_context",
    "test_scores",
    "activities",
    "honors",
    "essays",
    "recommendations",
    "target_colleges",
    "evaluations",
    "evaluation_components",
    "triggered_rules",
    "application_material_status",
    "saved_reports",
    "rate_limit_buckets",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in DOMAIN_TABLES:
        Base.metadata.tables[table_name].create(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in reversed(DOMAIN_TABLES):
        Base.metadata.tables[table_name].drop(bind, checkfirst=True)
