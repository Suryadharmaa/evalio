from pathlib import Path

import pytest

from scripts import import_college_batch
from scripts.import_college_batch import import_batch, parse_batch

DATA_ROOT = Path("data/data_v2/seed")


@pytest.fixture(scope="module")
def parsed_batch() -> import_college_batch.CollegeBatch:
    return parse_batch(DATA_ROOT)


def test_parses_batch_1_and_batch_2_as_separate_layers(
    parsed_batch: import_college_batch.CollegeBatch,
) -> None:
    assert len(parsed_batch.colleges) == 200
    assert len(parsed_batch.admissions) == 200
    assert len(parsed_batch.financial_aid) == 200
    assert len(parsed_batch.enrichment) == 100
    assert len(parsed_batch.requirements) == 1_064
    assert len(parsed_batch.media) == 3
    assert len(parsed_batch.sources) == 996


def test_batch_2a_preserves_unknowns_and_resolved_conflicts(
    parsed_batch: import_college_batch.CollegeBatch,
) -> None:
    enrichment = {row["slug"]: row for row in parsed_batch.enrichment}

    assert enrichment["purdue-university"]["application_fee_usd"] is None
    assert enrichment["carnegie-mellon-university"]["test_policy"] == "PROGRAM_DEPENDENT"
    assert enrichment["yale-university"]["test_policy"] == "REQUIRED"
    assert enrichment["texas-a-and-m-university"]["application_fee_usd"] == 90
    assert any("purdue-university" in warning for warning in parsed_batch.warnings)


def test_batch_2b_preserves_nuanced_policies(
    parsed_batch: import_college_batch.CollegeBatch,
) -> None:
    enrichment = {row["slug"]: row for row in parsed_batch.enrichment}

    assert enrichment["university-of-georgia"]["application_fee_usd"] is None
    assert (
        enrichment["university-of-miami"]["test_policy"]
        == "OPTIONAL_FOR_INTL_OUTSIDE_US"
    )
    assert (
        enrichment["clemson-university"]["need_policy"]
        == "NO_SCHOLARSHIPS_FOR_INTL_UNDERGRAD"
    )
    assert enrichment["university-of-tennessee-knoxville"]["test_policy"] == "REQUIRED"


def test_blank_values_remain_null(parsed_batch: import_college_batch.CollegeBatch) -> None:
    admissions = {row["slug"]: row for row in parsed_batch.admissions}
    aid = {row["slug"]: row for row in parsed_batch.financial_aid}

    assert admissions["princeton-university"]["sat_50"] is None
    assert admissions["princeton-university"]["application_fee_usd"] is None
    assert aid["samford-university"]["international_need_based_aid"] is None
    assert aid["samford-university"]["international_need_based_aid_status"] == "UNKNOWN"


def test_dry_run_never_connects_to_database(
    parsed_batch: import_college_batch.CollegeBatch, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        import_college_batch,
        "connect_database",
        lambda *_args, **_kwargs: pytest.fail("dry-run connected to database"),
    )

    report = import_batch(parsed_batch, dry_run=True)

    assert report.dry_run is True
    assert report.colleges_upserted == 200
    assert report.requirements_upserted == 1_064


def test_production_environment_is_always_rejected(
    parsed_batch: import_college_batch.CollegeBatch,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(ValueError, match="APP_ENV=production"):
        import_batch(parsed_batch, environment="staging")


def test_writes_require_explicit_local_or_staging_environment(
    parsed_batch: import_college_batch.CollegeBatch,
) -> None:
    with pytest.raises(ValueError, match="explicit --environment"):
        import_batch(parsed_batch)
