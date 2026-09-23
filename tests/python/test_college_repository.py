from typing import Any, cast

from sqlalchemy.dialects import postgresql

from api.admission_engine.repositories.colleges import CollegeRepository
from api.admission_engine.schemas.colleges import CollegeListParams


def test_cycle_sensitive_filters_use_only_latest_snapshots() -> None:
    repository = CollegeRepository(cast(Any, None))
    query = repository._filtered(
        CollegeListParams.model_validate({"test_policy": "OPTIONAL", "need_policy": "NEED_BLIND"})
    )
    sql = str(query.compile(dialect=postgresql.dialect()))  # type: ignore[no-untyped-call]

    assert sql.count("max(college_admissions.academic_cycle)") == 1
    assert sql.count("max(college_financial_aid.academic_cycle)") == 1


def test_filters_include_default_country_search_and_state() -> None:
    repository = CollegeRepository(cast(Any, None))
    query = repository._filtered(CollegeListParams(q="Harvard", state="MA"))
    compiled = query.compile(dialect=postgresql.dialect())  # type: ignore[no-untyped-call]

    assert "colleges.country_code" in str(compiled)
    assert "colleges.normalized_name LIKE" in str(compiled)
    assert "colleges.state_region" in str(compiled)
    assert {"US", "harvard", "MA"} <= set(compiled.params.values())


def test_pagination_uses_stable_order_offset_and_page_size() -> None:
    repository = CollegeRepository(cast(Any, None))
    params = CollegeListParams(page=3, page_size=10)
    query = repository._paginated(repository._filtered(params), params)
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    compiled = query.compile(
        dialect=dialect, compile_kwargs={"literal_binds": True}
    )
    sql = str(compiled)

    assert "ORDER BY colleges.name, colleges.id" in sql
    assert "LIMIT 10 OFFSET 20" in sql


def test_application_platform_filter_uses_jsonb_membership() -> None:
    repository = CollegeRepository(cast(Any, None))
    query = repository._filtered(CollegeListParams(application_platform="COMMON_APP"))
    compiled = query.compile(dialect=postgresql.dialect())  # type: ignore[no-untyped-call]

    assert "colleges.application_platforms" in str(compiled)
    assert compiled.params


def test_institution_and_selectivity_filters_use_latest_admission_rate() -> None:
    repository = CollegeRepository(cast(Any, None))
    query = repository._filtered(
        CollegeListParams(institution_type="PRIVATE_NONPROFIT", selectivity_band="UNDER_10")
    )
    sql = str(query.compile(dialect=postgresql.dialect()))  # type: ignore[no-untyped-call]
    assert "colleges.institution_type" in sql
    assert "college_admissions.acceptance_rate" in sql
    assert "ORDER BY college_admissions.academic_cycle DESC" in sql
