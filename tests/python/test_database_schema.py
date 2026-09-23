from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from api.admission_engine.database import models as _models  # noqa: F401
from api.admission_engine.database.base import Base


def test_complete_postgres_schema_compiles() -> None:
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    statements = [
        str(CreateTable(table).compile(dialect=dialect)) for table in Base.metadata.sorted_tables
    ]
    expected = {
        "users",
        "applicant_profiles",
        "academic_terms",
        "courses",
        "school_context",
        "test_scores",
        "activities",
        "honors",
        "essays",
        "essay_metrics",
        "recommendations",
        "colleges",
        "college_admissions",
        "college_requirements",
        "college_financial_aid",
        "college_cds_factors",
        "college_sources",
        "college_media",
        "target_colleges",
        "evaluations",
        "evaluation_components",
        "triggered_rules",
        "application_material_status",
        "saved_reports",
        "rate_limit_buckets",
        "admin_import_runs",
    }
    assert expected <= set(Base.metadata.tables)
    assert any("CREATE TABLE evaluations" in statement for statement in statements)
