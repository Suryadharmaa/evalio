import csv
import shutil
from pathlib import Path

import pytest

from scripts import import_college_refresh
from scripts.import_college_refresh import (
    RefreshValidationError,
    import_refresh,
    parse_refresh,
)

DATA_ROOT = Path("data/Update_Data")


@pytest.fixture(scope="module")
def parsed_refresh() -> import_college_refresh.CollegeRefresh:
    return parse_refresh(DATA_ROOT)


def test_parses_complete_refresh_without_using_legacy_identities(
    parsed_refresh: import_college_refresh.CollegeRefresh,
) -> None:
    assert len(parsed_refresh.wide) == 200
    assert len(parsed_refresh.identities) == 12
    assert len(parsed_refresh.admissions) == 12
    assert len(parsed_refresh.financial_aid) == 12
    assert len(parsed_refresh.sources) == 230
    assert any("legacy identity" in warning for warning in parsed_refresh.warnings)


def test_converts_rates_nulls_and_nuanced_booleans(
    parsed_refresh: import_college_refresh.CollegeRefresh,
) -> None:
    admissions = {row["slug"]: row for row in parsed_refresh.admissions}
    wide = {row["slug"]: row for row in parsed_refresh.wide}

    assert str(admissions["harvard-university"]["acceptance_rate"]) == "0.0418"
    assert admissions["harvard-university"]["sat_25"] is None
    assert wide["duke-university"]["international_need_based_aid"] is None
    assert (
        wide["duke-university"]["international_need_based_aid_status"]
        == "SELECTIVE"
    )
    assert wide["harvard-university"]["application_fee_status"] == "VERIFIED_GRID"


def test_preserves_new_detailed_cost_fields(
    parsed_refresh: import_college_refresh.CollegeRefresh,
) -> None:
    aid = {row["slug"]: row for row in parsed_refresh.financial_aid}
    princeton = aid["princeton-university"]

    assert princeton["css_profile_required"] is False
    assert str(princeton["books_personal"]) == "4050"
    assert str(princeton["estimated_cost_of_attendance"]) == "94624"


def test_sources_are_deduplicated_and_keep_provenance(
    parsed_refresh: import_college_refresh.CollegeRefresh,
) -> None:
    keys = {
        (
            row["slug"],
            row["field_group"],
            row["field_name"],
            row["source_url"],
            row["source_cycle"],
        )
        for row in parsed_refresh.sources
    }

    assert len(keys) == len(parsed_refresh.sources)
    assert any(
        row["slug"] == "harvard-university"
        and row["field_name"] == "admissions_profile"
        and row["confidence"] == "MEDIUM"
        and row["freshness"] == "CURRENT_OR_LATEST_AVAILABLE"
        for row in parsed_refresh.sources
    )


def test_dry_run_never_connects_to_database(
    parsed_refresh: import_college_refresh.CollegeRefresh,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        import_college_refresh,
        "connect_database",
        lambda *_args, **_kwargs: pytest.fail("dry-run connected to database"),
    )

    report = import_refresh(parsed_refresh, dry_run=True)

    assert report.dry_run is True
    assert report.policy_rows_updated == 200
    assert report.sources_upserted == 230


def test_production_environment_is_rejected(
    parsed_refresh: import_college_refresh.CollegeRefresh,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(ValueError, match="APP_ENV=production"):
        import_refresh(parsed_refresh, environment="staging")


def test_invalid_acceptance_rate_rejects_entire_refresh(tmp_path: Path) -> None:
    refresh_root = tmp_path / "Update_Data"
    shutil.copytree(DATA_ROOT, refresh_root)
    path = refresh_root / "admissions_UPDATED.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
        fieldnames = list(rows[0])
    rows[0]["acceptance_rate"] = "104"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(RefreshValidationError, match="acceptance"):
        parse_refresh(refresh_root)
