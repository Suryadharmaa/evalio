import csv
import uuid
from pathlib import Path
from typing import cast

import pytest

from scripts import import_colleges
from scripts.import_colleges import (
    ImportValidationError,
    import_dataset,
    parse_application_platforms,
    parse_csv,
    parse_nullable_boolean,
)

DATASET = Path("data/seed/evalio_top200_us_colleges_enriched.csv")


def base_row(**overrides: str) -> dict[str, str]:
    row = {
        "school_id": "example-university",
        "school_name": "Example University",
        "country_code": "US",
        "state_region": "CA",
        "city": "Example City",
        "institution_type": "PRIVATE_NONPROFIT",
        "application_platform_primary": "COMMON_APP",
        "application_platforms": "COMMON_APP;COALITION",
        "test_policy_2026_27": "OPTIONAL",
        "test_policy_status": "VERIFIED_2026_27_FAIRTEST",
        "international_aid_policy": "NEED_BLIND",
        "international_need_based_aid": "YES",
        "meets_full_demonstrated_need_international": "UNKNOWN",
        "aid_policy_status": "VERIFIED_CURRENT_OFFICIAL",
        "acceptance_rate": "12.5",
        "sat_25": "1200",
        "sat_50": "1300",
        "sat_75": "1400",
        "act_25": "28",
        "act_50": "30",
        "act_75": "32",
        "tuition_usd": "50000",
        "estimated_cost_of_attendance_usd": "75000",
        "admissions_metrics_status": "VERIFIED_LATEST_FEDERAL_SOURCE",
        "data_as_of": "2026-09-13",
        "identity_confidence": "HIGH",
        "collegedata_search_url": "https://example.test/search",
        "test_policy_source_url": "https://example.edu/testing",
        "aid_policy_source_url": "https://example.edu/aid",
        "current_data_reference": "https://collegescorecard.ed.gov/school/?1",
        "notes": "",
    }
    row.update(overrides)
    return row


def write_rows(path: Path, rows: list[dict[str, str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(base_row()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_csv_parsing_maps_the_bundled_200_rows() -> None:
    dataset = parse_csv(DATASET)

    assert len(dataset.rows) == 200
    assert dataset.rows[0].slug == "princeton-university"
    assert dataset.rows[0].acceptance_rate is not None


def test_blank_numbers_become_null(tmp_path: Path) -> None:
    path = write_rows(
        tmp_path / "blank.csv",
        [base_row(acceptance_rate="", sat_50="", tuition_usd="")],
    )

    row = parse_csv(path, expected_rows=None).rows[0]

    assert row.acceptance_rate is None
    assert row.sat_50 is None
    assert row.tuition is None


def test_boolean_conversion() -> None:
    assert parse_nullable_boolean("YES") is True
    assert parse_nullable_boolean("NO") is False
    assert parse_nullable_boolean("UNKNOWN") is None
    with pytest.raises(ImportValidationError):
        parse_nullable_boolean("MAYBE")


def test_invalid_enum_is_rejected(tmp_path: Path) -> None:
    path = write_rows(tmp_path / "bad-enum.csv", [base_row(test_policy_2026_27="MAYBE")])

    with pytest.raises(ImportValidationError, match="invalid value MAYBE"):
        parse_csv(path, expected_rows=None)


def test_duplicate_school_ids_are_rejected(tmp_path: Path) -> None:
    path = write_rows(
        tmp_path / "duplicate.csv",
        [base_row(), base_row(school_name="Second University")],
    )

    with pytest.raises(ImportValidationError, match="duplicate value example-university"):
        parse_csv(path, expected_rows=None)


@pytest.mark.parametrize(
    ("field", "value"),
    [("sat_25", "399"), ("sat_75", "1601"), ("act_25", "0"), ("act_75", "37")],
)
def test_invalid_sat_and_act_are_rejected(tmp_path: Path, field: str, value: str) -> None:
    path = write_rows(tmp_path / f"bad-{field}.csv", [base_row(**{field: value})])

    with pytest.raises(ImportValidationError, match="outside allowed range"):
        parse_csv(path, expected_rows=None)


def test_invalid_acceptance_rate_is_rejected(tmp_path: Path) -> None:
    path = write_rows(tmp_path / "bad-rate.csv", [base_row(acceptance_rate="100.1")])

    with pytest.raises(ImportValidationError, match="outside allowed range"):
        parse_csv(path, expected_rows=None)


def test_application_platform_conversion() -> None:
    assert parse_application_platforms("COMMON_APP; COALITION;COMMON_APP") == [
        "COMMON_APP",
        "COALITION",
    ]
    with pytest.raises(ImportValidationError, match="INVALID_PLATFORM"):
        parse_application_platforms("INVALID_PLATFORM")


def test_source_records_are_only_created_for_nonblank_urls(tmp_path: Path) -> None:
    path = write_rows(
        tmp_path / "sources.csv",
        [base_row(aid_policy_source_url="", current_data_reference="")],
    )

    sources = parse_csv(path, expected_rows=None).rows[0].sources

    assert {source.field_name for source in sources} == {"college_profile", "test_policy"}


def test_dry_run_never_opens_a_database_connection(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dataset = parse_csv(write_rows(tmp_path / "dry.csv", [base_row()]), expected_rows=None)
    monkeypatch.setattr(
        import_colleges,
        "connect_database",
        lambda *_args, **_kwargs: pytest.fail("dry run attempted a database connection"),
    )

    report = import_dataset(dataset, dry_run=True)

    assert report.dry_run is True
    assert report.planned_college_upserts == 1
    assert report.colleges_inserted == 0


class FakeCursor:
    def __init__(self) -> None:
        self.colleges: dict[str, uuid.UUID] = {}
        self.admissions: set[tuple[uuid.UUID, str]] = set()
        self.aid: set[tuple[uuid.UUID, str]] = set()
        self.sources: dict[tuple[object, ...], uuid.UUID] = {}
        self.result: tuple[object, ...] | None = None

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, query: str, params: tuple[object, ...]) -> None:
        sql = " ".join(query.split()).lower()
        self.result = None
        if sql.startswith("select 1 from colleges"):
            self.result = (1,) if params[0] in self.colleges else None
        elif sql.startswith("insert into colleges"):
            college_id = self.colleges.setdefault(str(params[1]), uuid.uuid4())
            self.result = (college_id,)
        elif sql.startswith("select 1 from college_admissions"):
            self.result = (1,) if (params[0], params[1]) in self.admissions else None
        elif sql.startswith("insert into college_admissions"):
            self.admissions.add((cast(uuid.UUID, params[1]), str(params[2])))
        elif sql.startswith("select 1 from college_financial_aid"):
            self.result = (1,) if (params[0], params[1]) in self.aid else None
        elif sql.startswith("insert into college_financial_aid"):
            self.aid.add((cast(uuid.UUID, params[1]), str(params[2])))
        elif sql.startswith("select id from college_sources"):
            self.result = (self.sources[params],) if params in self.sources else None
        elif sql.startswith("insert into college_sources"):
            key = (params[1], params[2], params[3], params[5], params[6])
            self.sources[key] = uuid.uuid4()

    def fetchone(self) -> tuple[object, ...] | None:
        return self.result


class FakeConnection:
    def __init__(self) -> None:
        self.fake_cursor = FakeCursor()

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return self.fake_cursor


def test_upsert_is_idempotent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dataset = parse_csv(write_rows(tmp_path / "upsert.csv", [base_row()]), expected_rows=None)
    connection = FakeConnection()
    monkeypatch.setattr(import_colleges, "connect_database", lambda *_args: connection)

    first = import_dataset(dataset, database_url="postgresql://test")
    second = import_dataset(dataset, database_url="postgresql://test")

    assert (first.colleges_inserted, first.colleges_updated) == (1, 0)
    assert (second.colleges_inserted, second.colleges_updated) == (0, 1)
    assert (len(connection.fake_cursor.colleges), len(connection.fake_cursor.admissions)) == (1, 1)
    assert len(connection.fake_cursor.aid) == 1
    assert len(connection.fake_cursor.sources) == 4
