"""Validate and transactionally import Evalio's enriched college CSV."""

from __future__ import annotations

import argparse
import csv
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import psycopg
from psycopg.types.json import Jsonb

from api.admission_engine.config import get_settings

connect_database = psycopg.connect

ACADEMIC_CYCLE = "2026-27"
EXPECTED_ROWS = 200
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEST_POLICIES = {"REQUIRED", "OPTIONAL", "FLEXIBLE", "BLIND", "NOT_ACCEPTED", "UNKNOWN"}
NEED_POLICIES = {"NEED_BLIND", "NEED_AWARE", "NO_NEED_BASED_AID", "UNKNOWN"}
INSTITUTION_TYPES = {"PUBLIC", "PRIVATE_NONPROFIT", "PRIVATE_FOR_PROFIT", "UNKNOWN"}
APPLICATION_PLATFORMS = {
    "COMMON_APP", "COALITION", "INSTITUTIONAL", "UC_APPLICATION", "CAL_STATE_APPLY",
    "APPLYTEXAS", "SUNY", "SUNY_APPLICATION", "OTHER", "UNKNOWN",
}
CONFIDENCE_VALUES = {"HIGH", "MEDIUM", "LOW"}
REQUIRED_COLUMNS = {
    "school_id", "school_name", "country_code", "state_region", "city",
    "institution_type", "application_platform_primary", "application_platforms",
    "test_policy_2026_27", "international_aid_policy",
    "international_need_based_aid", "meets_full_demonstrated_need_international",
    "acceptance_rate", "sat_25", "sat_50", "sat_75", "act_25", "act_50", "act_75",
    "tuition_usd", "estimated_cost_of_attendance_usd", "data_as_of",
    "identity_confidence", "collegedata_search_url", "test_policy_source_url",
    "aid_policy_source_url", "current_data_reference",
}


class ImportValidationError(ValueError):
    def __init__(self, errors: list[str], *, rows_read: int = 0) -> None:
        super().__init__("College CSV validation failed:\n- " + "\n- ".join(errors))
        self.errors = errors
        self.rows_read = rows_read


@dataclass(frozen=True)
class SourceRecord:
    field_group: str
    field_name: str
    source_type: str
    source_url: str
    retrieved_at: datetime
    verified_at: datetime | None
    freshness: str
    confidence: str


@dataclass(frozen=True)
class CollegeRow:
    slug: str
    name: str
    normalized_name: str
    country_code: str
    state_region: str | None
    city: str | None
    institution_type: str
    application_platform_primary: str
    application_platforms: list[str]
    acceptance_rate: Decimal | None
    sat_25: Decimal | None
    sat_50: Decimal | None
    sat_75: Decimal | None
    act_25: Decimal | None
    act_50: Decimal | None
    act_75: Decimal | None
    test_policy: str
    tuition: Decimal | None
    estimated_cost_of_attendance: Decimal | None
    need_policy: str
    international_need_based_aid: bool | None
    meets_full_demonstrated_need: bool | None
    notes: str | None
    sources: list[SourceRecord]


@dataclass(frozen=True)
class CollegeDataset:
    rows: list[CollegeRow]
    warnings: list[str] = field(default_factory=list)


@dataclass
class ImportReport:
    rows_read: int
    valid_rows: int
    rejected_rows: int = 0
    warnings: int = 0
    colleges_inserted: int = 0
    colleges_updated: int = 0
    admissions_inserted: int = 0
    admissions_updated: int = 0
    financial_aid_inserted: int = 0
    financial_aid_updated: int = 0
    source_records_inserted: int = 0
    source_records_updated: int = 0
    dry_run: bool = False
    planned_college_upserts: int = 0
    planned_admissions_upserts: int = 0
    planned_financial_aid_upserts: int = 0
    planned_source_upserts: int = 0


def parse_nullable_boolean(value: str, label: str = "value") -> bool | None:
    normalized = value.strip().upper()
    if normalized == "YES":
        return True
    if normalized == "NO":
        return False
    if normalized in {"", "UNKNOWN"}:
        return None
    raise ImportValidationError([f"{label}: expected YES, NO, or UNKNOWN"])


def parse_application_platforms(value: str, label: str = "application_platforms") -> list[str]:
    platforms = list(dict.fromkeys(item.strip().upper() for item in value.split(";") if item.strip()))
    invalid = [item for item in platforms if item not in APPLICATION_PLATFORMS]
    if invalid:
        raise ImportValidationError([f"{label}: invalid value(s): {', '.join(invalid)}"])
    return platforms


def _optional_decimal(
    value: str, label: str, *, minimum: Decimal, maximum: Decimal | None = None
) -> Decimal | None:
    if not value.strip():
        return None
    try:
        parsed = Decimal(value.strip())
    except InvalidOperation as exc:
        raise ImportValidationError([f"{label}: expected a number"]) from exc
    if not parsed.is_finite() or parsed < minimum or (maximum is not None and parsed > maximum):
        raise ImportValidationError([f"{label}: outside allowed range"])
    return parsed


def _required(value: str, label: str) -> str:
    result = value.strip()
    if not result:
        raise ImportValidationError([f"{label}: required"])
    return result


def _enum(value: str, allowed: set[str], label: str) -> str:
    result = _required(value, label).upper()
    if result not in allowed:
        raise ImportValidationError([f"{label}: invalid value {result}"])
    return result


def _url(value: str, label: str) -> str | None:
    result = value.strip()
    if not result:
        return None
    parsed = urlparse(result)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ImportValidationError([f"{label}: invalid web URL"])
    return result


def _date(value: str, label: str) -> datetime:
    try:
        return datetime.fromisoformat(_required(value, label)).replace(tzinfo=UTC)
    except ValueError as exc:
        raise ImportValidationError([f"{label}: invalid ISO date"]) from exc


def _source_records(
    raw: dict[str, str], retrieved_at: datetime, confidence: str
) -> list[SourceRecord]:
    specs = (
        ("collegedata_search_url", "IDENTITY", "college_profile", "COLLEGE_DATA", True),
        (
            "test_policy_source_url", "ADMISSIONS", "test_policy", "OFFICIAL",
            raw.get("test_policy_status", "").upper().startswith("VERIFIED"),
        ),
        (
            "aid_policy_source_url", "FINANCIAL_AID", "need_policy", "OFFICIAL",
            raw.get("aid_policy_status", "").upper().startswith("VERIFIED"),
        ),
        (
            "current_data_reference", "ADMISSIONS", "admissions_metrics", "COLLEGE_SCORECARD",
            raw.get("admissions_metrics_status", "").upper().startswith("VERIFIED"),
        ),
    )
    records: list[SourceRecord] = []
    for column, group, field_name, source_type, verified in specs:
        url = _url(raw.get(column, ""), column)
        if url is not None:
            records.append(
                SourceRecord(
                    field_group=group,
                    field_name=field_name,
                    source_type=source_type,
                    source_url=url,
                    retrieved_at=retrieved_at,
                    verified_at=retrieved_at if verified else None,
                    freshness="CURRENT" if verified else "REVIEW_SOON",
                    confidence=confidence,
                )
            )
    return records


def _parse_row(raw: dict[str, str], line_number: int) -> CollegeRow:
    label = f"line {line_number}"
    slug = _required(raw.get("school_id", ""), f"{label} school_id")
    if not SLUG_PATTERN.fullmatch(slug):
        raise ImportValidationError([f"{label} school_id: invalid slug"])
    name = _required(raw.get("school_name", ""), f"{label} school_name")
    country = _required(raw.get("country_code", ""), f"{label} country_code").upper()
    if len(country) != 2 or not country.isalpha():
        raise ImportValidationError([f"{label} country_code: expected two letters"])
    institution_type = _enum(
        raw.get("institution_type", ""), INSTITUTION_TYPES, f"{label} institution_type"
    )
    primary_platform = _enum(
        raw.get("application_platform_primary", ""),
        APPLICATION_PLATFORMS,
        f"{label} application_platform_primary",
    )
    platforms = parse_application_platforms(
        raw.get("application_platforms", ""), f"{label} application_platforms"
    )
    if primary_platform not in platforms:
        raise ImportValidationError(
            [f"{label} application_platform_primary: must be present in application_platforms"]
        )
    acceptance_percent = _optional_decimal(
        raw.get("acceptance_rate", ""),
        f"{label} acceptance_rate",
        minimum=Decimal(0),
        maximum=Decimal(100),
    )
    retrieved_at = _date(raw.get("data_as_of", ""), f"{label} data_as_of")
    confidence = _enum(
        raw.get("identity_confidence", ""), CONFIDENCE_VALUES, f"{label} identity_confidence"
    )
    row = CollegeRow(
        slug=slug,
        name=name,
        normalized_name=" ".join(name.casefold().split()),
        country_code=country,
        state_region=raw.get("state_region", "").strip().upper() or None,
        city=raw.get("city", "").strip() or None,
        institution_type=institution_type,
        application_platform_primary=primary_platform,
        application_platforms=platforms,
        acceptance_rate=acceptance_percent / Decimal(100) if acceptance_percent is not None else None,
        sat_25=_optional_decimal(raw.get("sat_25", ""), f"{label} sat_25", minimum=Decimal(400), maximum=Decimal(1600)),
        sat_50=_optional_decimal(raw.get("sat_50", ""), f"{label} sat_50", minimum=Decimal(400), maximum=Decimal(1600)),
        sat_75=_optional_decimal(raw.get("sat_75", ""), f"{label} sat_75", minimum=Decimal(400), maximum=Decimal(1600)),
        act_25=_optional_decimal(raw.get("act_25", ""), f"{label} act_25", minimum=Decimal(1), maximum=Decimal(36)),
        act_50=_optional_decimal(raw.get("act_50", ""), f"{label} act_50", minimum=Decimal(1), maximum=Decimal(36)),
        act_75=_optional_decimal(raw.get("act_75", ""), f"{label} act_75", minimum=Decimal(1), maximum=Decimal(36)),
        test_policy=_enum(raw.get("test_policy_2026_27", ""), TEST_POLICIES, f"{label} test_policy_2026_27"),
        tuition=_optional_decimal(raw.get("tuition_usd", ""), f"{label} tuition_usd", minimum=Decimal(0)),
        estimated_cost_of_attendance=_optional_decimal(
            raw.get("estimated_cost_of_attendance_usd", ""),
            f"{label} estimated_cost_of_attendance_usd",
            minimum=Decimal(0),
        ),
        need_policy=_enum(raw.get("international_aid_policy", ""), NEED_POLICIES, f"{label} international_aid_policy"),
        international_need_based_aid=parse_nullable_boolean(
            raw.get("international_need_based_aid", ""), f"{label} international_need_based_aid"
        ),
        meets_full_demonstrated_need=parse_nullable_boolean(
            raw.get("meets_full_demonstrated_need_international", ""),
            f"{label} meets_full_demonstrated_need_international",
        ),
        notes=raw.get("notes", "").strip() or None,
        sources=_source_records(raw, retrieved_at, confidence),
    )
    for prefix in ("sat", "act"):
        values = [getattr(row, f"{prefix}_{percentile}") for percentile in (25, 50, 75)]
        present = [value for value in values if value is not None]
        if present != sorted(present):
            raise ImportValidationError([f"{label}: invalid {prefix.upper()} percentile order"])
    return row


def parse_csv(path: Path, *, expected_rows: int | None = EXPECTED_ROWS) -> CollegeDataset:
    if not path.is_file():
        raise ImportValidationError([f"file not found: {path}"])
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - headers)
        if missing:
            raise ImportValidationError([f"missing columns: {', '.join(missing)}"])
        raw_rows = [
            {key: (value or "").strip() for key, value in raw.items() if key is not None}
            for raw in reader
        ]

    errors: list[str] = []
    rows: list[CollegeRow] = []
    if expected_rows is not None and len(raw_rows) != expected_rows:
        errors.append(f"dataset must contain exactly {expected_rows} rows; found {len(raw_rows)}")
    for line_number, raw in enumerate(raw_rows, 2):
        try:
            rows.append(_parse_row(raw, line_number))
        except ImportValidationError as exc:
            errors.extend(exc.errors)

    seen_slugs: set[str] = set()
    seen_names: set[str] = set()
    for line_number, row in enumerate(rows, 2):
        if row.slug in seen_slugs:
            errors.append(f"line {line_number} school_id: duplicate value {row.slug}")
        seen_slugs.add(row.slug)
        if row.normalized_name in seen_names:
            errors.append(f"line {line_number} school_name: duplicate value {row.name}")
        seen_names.add(row.normalized_name)
    if errors:
        raise ImportValidationError(errors, rows_read=len(raw_rows))

    missing_numeric = sum(
        value is None
        for row in rows
        for value in (
            row.acceptance_rate, row.sat_25, row.sat_50, row.sat_75,
            row.act_25, row.act_50, row.act_75, row.tuition,
            row.estimated_cost_of_attendance,
        )
    )
    unknown_categories = sum(
        row.test_policy == "UNKNOWN" or row.need_policy == "UNKNOWN" for row in rows
    )
    nullable_unknowns = sum(
        value is None
        for row in rows
        for value in (row.international_need_based_aid, row.meets_full_demonstrated_need)
    )
    warnings: list[str] = []
    if missing_numeric:
        warnings.append(f"{missing_numeric} blank numeric values will remain NULL")
    if unknown_categories:
        warnings.append(f"{unknown_categories} rows contain an UNKNOWN policy")
    if nullable_unknowns:
        warnings.append(f"{nullable_unknowns} UNKNOWN boolean values will remain NULL")
    return CollegeDataset(rows=rows, warnings=warnings)


def _database_url() -> str:
    value = get_settings().DATABASE_URL
    if value is None:
        raise ValueError("DATABASE_URL is required")
    return value.get_secret_value().replace("postgresql+psycopg://", "postgresql://", 1)


def _exists(cursor: Any, query: str, params: tuple[object, ...]) -> bool:
    cursor.execute(query, params)
    return cursor.fetchone() is not None


def import_dataset(
    dataset: CollegeDataset, *, database_url: str | None = None, dry_run: bool = False
) -> ImportReport:
    source_count = sum(len(row.sources) for row in dataset.rows)
    report = ImportReport(
        rows_read=len(dataset.rows), valid_rows=len(dataset.rows), warnings=len(dataset.warnings),
        dry_run=dry_run, planned_college_upserts=len(dataset.rows),
        planned_admissions_upserts=len(dataset.rows),
        planned_financial_aid_upserts=len(dataset.rows), planned_source_upserts=source_count,
    )
    if dry_run:
        return report

    now = datetime.now(UTC)
    with connect_database(database_url or _database_url()) as connection, connection.cursor() as cursor:
        for row in dataset.rows:
            college_exists = _exists(cursor, "SELECT 1 FROM colleges WHERE slug = %s", (row.slug,))
            cursor.execute(
                """
                INSERT INTO colleges
                    (id, slug, name, normalized_name, country_code, state_region, city,
                     institution_type, application_platform_primary, application_platforms,
                     common_app_member, active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name, normalized_name = EXCLUDED.normalized_name,
                    country_code = EXCLUDED.country_code, state_region = EXCLUDED.state_region,
                    city = EXCLUDED.city, institution_type = EXCLUDED.institution_type,
                    application_platform_primary = EXCLUDED.application_platform_primary,
                    application_platforms = EXCLUDED.application_platforms,
                    common_app_member = EXCLUDED.common_app_member, active = TRUE,
                    updated_at = EXCLUDED.updated_at
                RETURNING id
                """,
                (
                    uuid.uuid4(), row.slug, row.name, row.normalized_name, row.country_code,
                    row.state_region, row.city, row.institution_type,
                    row.application_platform_primary, Jsonb(row.application_platforms),
                    "COMMON_APP" in row.application_platforms, now, now,
                ),
            )
            college_id = cursor.fetchone()[0]
            if college_exists:
                report.colleges_updated += 1
            else:
                report.colleges_inserted += 1

            admission_exists = _exists(
                cursor,
                "SELECT 1 FROM college_admissions WHERE college_id = %s AND academic_cycle = %s",
                (college_id, ACADEMIC_CYCLE),
            )
            cursor.execute(
                """
                INSERT INTO college_admissions
                    (id, college_id, academic_cycle, acceptance_rate, sat_25, sat_50, sat_75,
                     act_25, act_50, act_75, test_policy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (college_id, academic_cycle) DO UPDATE SET
                    acceptance_rate = EXCLUDED.acceptance_rate, sat_25 = EXCLUDED.sat_25,
                    sat_50 = EXCLUDED.sat_50, sat_75 = EXCLUDED.sat_75,
                    act_25 = EXCLUDED.act_25, act_50 = EXCLUDED.act_50,
                    act_75 = EXCLUDED.act_75, test_policy = EXCLUDED.test_policy
                """,
                (
                    uuid.uuid4(), college_id, ACADEMIC_CYCLE, row.acceptance_rate,
                    row.sat_25, row.sat_50, row.sat_75, row.act_25, row.act_50,
                    row.act_75, row.test_policy,
                ),
            )
            if admission_exists:
                report.admissions_updated += 1
            else:
                report.admissions_inserted += 1

            aid_exists = _exists(
                cursor,
                "SELECT 1 FROM college_financial_aid WHERE college_id = %s AND academic_cycle = %s",
                (college_id, ACADEMIC_CYCLE),
            )
            cursor.execute(
                """
                INSERT INTO college_financial_aid
                    (id, college_id, academic_cycle, need_policy, international_need_based_aid,
                     meets_full_demonstrated_need, estimated_cost_of_attendance, tuition,
                     currency, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'USD', %s)
                ON CONFLICT (college_id, academic_cycle) DO UPDATE SET
                    need_policy = EXCLUDED.need_policy,
                    international_need_based_aid = EXCLUDED.international_need_based_aid,
                    meets_full_demonstrated_need = EXCLUDED.meets_full_demonstrated_need,
                    estimated_cost_of_attendance = EXCLUDED.estimated_cost_of_attendance,
                    tuition = EXCLUDED.tuition, currency = EXCLUDED.currency,
                    notes = EXCLUDED.notes
                """,
                (
                    uuid.uuid4(), college_id, ACADEMIC_CYCLE, row.need_policy,
                    row.international_need_based_aid, row.meets_full_demonstrated_need,
                    row.estimated_cost_of_attendance, row.tuition, row.notes,
                ),
            )
            if aid_exists:
                report.financial_aid_updated += 1
            else:
                report.financial_aid_inserted += 1

            for source in row.sources:
                cursor.execute(
                    """
                    SELECT id FROM college_sources
                    WHERE college_id = %s AND field_group = %s AND field_name = %s
                      AND source_url = %s AND academic_cycle = %s
                    """,
                    (
                        college_id, source.field_group, source.field_name,
                        source.source_url, ACADEMIC_CYCLE,
                    ),
                )
                existing_source = cursor.fetchone()
                if existing_source is None:
                    cursor.execute(
                        """
                        INSERT INTO college_sources
                            (id, college_id, field_group, field_name, source_type, source_url,
                             academic_cycle, retrieved_at, verified_at, freshness, confidence)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            uuid.uuid4(), college_id, source.field_group, source.field_name,
                            source.source_type, source.source_url, ACADEMIC_CYCLE,
                            source.retrieved_at, source.verified_at, source.freshness,
                            source.confidence,
                        ),
                    )
                    report.source_records_inserted += 1
                else:
                    cursor.execute(
                        """
                        UPDATE college_sources SET source_type = %s, retrieved_at = %s,
                            verified_at = %s, freshness = %s, confidence = %s
                        WHERE id = %s
                        """,
                        (
                            source.source_type, source.retrieved_at, source.verified_at,
                            source.freshness, source.confidence, existing_source[0],
                        ),
                    )
                    report.source_records_updated += 1
    return report


def _print_report(report: ImportReport, warnings: list[str]) -> None:
    print(f"rows read: {report.rows_read}")
    print(f"valid rows: {report.valid_rows}")
    print(f"rejected rows: {report.rejected_rows}")
    print(f"warnings: {report.warnings}")
    for warning in warnings:
        print(f"  - {warning}")
    print(f"colleges inserted: {report.colleges_inserted}")
    print(f"colleges updated: {report.colleges_updated}")
    print(f"admissions inserted/updated: {report.admissions_inserted}/{report.admissions_updated}")
    print(
        "financial aid inserted/updated: "
        f"{report.financial_aid_inserted}/{report.financial_aid_updated}"
    )
    print(
        "source records inserted/updated: "
        f"{report.source_records_inserted}/{report.source_records_updated}"
    )
    if report.dry_run:
        print(
            "dry-run planned upserts: "
            f"colleges={report.planned_college_upserts}, "
            f"admissions={report.planned_admissions_upserts}, "
            f"financial_aid={report.planned_financial_aid_upserts}, "
            f"sources={report.planned_source_upserts}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm", choices=("IMPORT",))
    args = parser.parse_args()
    dataset = parse_csv(args.file)
    if not args.dry_run and args.confirm != "IMPORT":
        parser.error("database writes require --confirm IMPORT")
    report = import_dataset(dataset, dry_run=args.dry_run)
    _print_report(report, dataset.warnings)


if __name__ == "__main__":
    main()
