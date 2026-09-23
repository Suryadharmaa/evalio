"""Local, explicit college-data staging workflow. Never run from public requests."""

import argparse
import csv
import hashlib
import json
import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import psycopg

STAGING_ROOT = Path(".evalio-staging")
REQUIRED_FIELDS = ("name", "slug", "country_code", "source_url")
MAX_SOURCE_BYTES = 50 * 1024 * 1024
MAX_IMPORT_ROWS = 100_000
RUN_ID_PATTERN = re.compile(r"^[a-f0-9]{16}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CYCLE_PATTERN = re.compile(r"^(20\d{2})-(?:20)?(\d{2})$")
TEST_POLICIES = frozenset({"REQUIRED", "OPTIONAL", "FLEXIBLE", "BLIND", "NOT_ACCEPTED", "UNKNOWN"})


def _safe_web_url(value: object) -> bool:
    parsed = urlparse(str(value))
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
    )


def _read_rows(source: Path) -> list[dict[str, Any]]:
    if not source.is_file():
        raise ValueError("Import source does not exist")
    if source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("Import source must be 50 MB or smaller")
    if source.suffix.lower() == ".json":
        value = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            raise ValueError("JSON import must contain a list of records")
        rows = [dict(row) for row in value]
    elif source.suffix.lower() == ".csv":
        with source.open(encoding="utf-8-sig", newline="") as stream:
            rows = [dict(row) for row in csv.DictReader(stream)]
    else:
        raise ValueError("Import source must be JSON or CSV")
    if len(rows) > MAX_IMPORT_ROWS:
        raise ValueError("Import source may contain at most 100,000 rows")
    return rows


def _run_path(run_id: str) -> Path:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("Invalid staging run ID")
    return STAGING_ROOT / f"{run_id}.json"


def import_rows(source: Path, cycle: str) -> str:
    rows = _read_rows(source)
    run_id = hashlib.sha256(
        f"{source.resolve()}:{cycle}:{datetime.now(UTC).isoformat()}".encode()
    ).hexdigest()[:16]
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    record = {
        "run_id": run_id,
        "status": "IMPORTED",
        "academic_cycle": cycle,
        "source_file": source.name,
        "rows": rows,
        "rows_read": len(rows),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _run_path(run_id).write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return run_id


def load_run(run_id: str) -> dict[str, Any]:
    return json.loads(_run_path(run_id).read_text(encoding="utf-8"))


def save_run(record: dict[str, Any]) -> None:
    _run_path(record["run_id"]).write_text(
        json.dumps(record, indent=2, sort_keys=True), encoding="utf-8"
    )


def validate(run_id: str) -> dict[str, Any]:
    record = load_run(run_id)
    errors: list[dict[str, Any]] = []
    cycle_match = CYCLE_PATTERN.fullmatch(str(record.get("academic_cycle", "")))
    cycle_start = int(cycle_match.group(1)) if cycle_match else None
    cycle_end = int(cycle_match.group(2)) if cycle_match else None
    if cycle_start is None or cycle_end != (cycle_start + 1) % 100:
        errors.append({"row": 0, "error": "invalid_academic_cycle"})
    elif cycle_start < datetime.now(UTC).year - 1:
        errors.append({"row": 0, "error": "stale_academic_cycle"})
    seen_slugs: set[str] = set()
    for index, row in enumerate(record["rows"]):
        missing = [field for field in REQUIRED_FIELDS if not str(row.get(field, "")).strip()]
        if missing:
            errors.append({"row": index + 1, "error": "missing_fields", "fields": missing})
        elif not _safe_web_url(row.get("source_url")):
            errors.append({"row": index + 1, "error": "invalid_source_url"})
        slug = str(row.get("slug", ""))
        if slug and not SLUG_PATTERN.fullmatch(slug):
            errors.append({"row": index + 1, "error": "invalid_slug"})
        country_code = str(row.get("country_code", ""))
        if country_code and (len(country_code) != 2 or not country_code.isalpha()):
            errors.append({"row": index + 1, "error": "invalid_country_code"})
        test_policy = str(row.get("test_policy") or "UNKNOWN").upper()
        if test_policy not in TEST_POLICIES:
            errors.append({"row": index + 1, "error": "unknown_test_policy"})
        if row.get("official_website") and not _safe_web_url(row.get("official_website")):
            errors.append({"row": index + 1, "error": "invalid_official_website"})
        if slug in seen_slugs:
            errors.append({"row": index + 1, "error": "duplicate_slug", "slug": slug})
        seen_slugs.add(slug)
        if row.get("acceptance_rate") not in (None, ""):
            try:
                rate = float(row["acceptance_rate"])
            except (TypeError, ValueError):
                rate = -1
            if not 0 <= rate <= 1:
                errors.append({"row": index + 1, "error": "invalid_admit_rate"})
        percentiles = [row.get(name) for name in ("sat_25", "sat_50", "sat_75")]
        if all(value not in (None, "") for value in percentiles):
            try:
                valid_percentiles = (
                    400
                    <= float(percentiles[0])
                    <= float(percentiles[1])
                    <= float(percentiles[2])
                    <= 1600
                )
            except (TypeError, ValueError):
                valid_percentiles = False
            if not valid_percentiles:
                errors.append({"row": index + 1, "error": "invalid_sat_percentile_order"})
    cycle_rejected = any(error["row"] == 0 for error in errors)
    rejected_rows = {error["row"] for error in errors if error["row"] > 0}
    record.update(
        status="VALID" if not errors else "REJECTED",
        validation_errors=errors,
        rows_valid=0 if cycle_rejected else len(record["rows"]) - len(rejected_rows),
        rows_rejected=len(record["rows"]) if cycle_rejected else len(rejected_rows),
    )
    save_run(record)
    return record


def approve(run_id: str, confirmation: str) -> dict[str, Any]:
    record = load_run(run_id)
    if record.get("status") != "VALID":
        raise ValueError("Only a valid import can be approved")
    if confirmation != "APPROVE":
        raise ValueError("Explicit --confirm APPROVE is required")
    record.update(status="APPROVED", approved_at=datetime.now(UTC).isoformat())
    save_run(record)
    return record


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL", "").strip()
    if not value:
        raise ValueError("DATABASE_URL is required for diff and promotion")
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def diff(run_id: str) -> dict[str, Any]:
    record = load_run(run_id)
    rows = record["rows"]
    slugs = [str(row["slug"]) for row in rows]
    with psycopg.connect(_database_url()) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT slug, name, country_code, state_region, institution_type, official_website "
            "FROM colleges WHERE slug = ANY(%s)",
            (slugs,),
        )
        current = {row[0]: row[1:] for row in cursor.fetchall()}
    changed = 0
    unchanged = 0
    for row in rows:
        existing = current.get(str(row["slug"]))
        proposed = (
            str(row["name"]),
            str(row["country_code"]).upper(),
            row.get("state_region") or None,
            row.get("institution_type") or None,
            row.get("official_website") or None,
        )
        if existing is None:
            continue
        if existing == proposed:
            unchanged += 1
        else:
            changed += 1
    summary = {"new": len(rows) - len(current), "changed": changed, "unchanged": unchanged}
    record["diff_summary"] = summary
    save_run(record)
    return {"run_id": run_id, **summary}


def promote(run_id: str, confirmation: str) -> dict[str, Any]:
    record = load_run(run_id)
    if record.get("status") != "APPROVED":
        raise ValueError("Import must be approved before promotion")
    if confirmation != "PROMOTE":
        raise ValueError("Explicit --confirm PROMOTE is required")
    now = datetime.now(UTC)
    with psycopg.connect(_database_url()) as connection, connection.cursor() as cursor:
        for row in record["rows"]:
            college_id = uuid.uuid4()
            cursor.execute(
                """
                INSERT INTO colleges
                    (id, slug, name, normalized_name, country_code, state_region,
                     institution_type, official_website, active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    normalized_name = EXCLUDED.normalized_name,
                    country_code = EXCLUDED.country_code,
                    state_region = EXCLUDED.state_region,
                    institution_type = EXCLUDED.institution_type,
                    official_website = EXCLUDED.official_website,
                    active = TRUE,
                    updated_at = EXCLUDED.updated_at
                RETURNING id
                """,
                (
                    college_id,
                    row["slug"],
                    row["name"],
                    str(row["name"]).casefold(),
                    str(row["country_code"]).upper(),
                    row.get("state_region") or None,
                    row.get("institution_type") or None,
                    row.get("official_website") or None,
                    now,
                    now,
                ),
            )
            persisted_id = cursor.fetchone()[0]
            if any(
                row.get(key) not in (None, "")
                for key in (
                    "acceptance_rate",
                    "sat_25",
                    "sat_50",
                    "sat_75",
                    "act_25",
                    "act_50",
                    "act_75",
                )
            ):
                cursor.execute(
                    """
                    INSERT INTO college_admissions
                        (id, college_id, academic_cycle, acceptance_rate, sat_25, sat_50,
                         sat_75, act_25, act_50, act_75, test_policy)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (college_id, academic_cycle) DO UPDATE SET
                        acceptance_rate = EXCLUDED.acceptance_rate,
                        sat_25 = EXCLUDED.sat_25, sat_50 = EXCLUDED.sat_50,
                        sat_75 = EXCLUDED.sat_75, act_25 = EXCLUDED.act_25,
                        act_50 = EXCLUDED.act_50, act_75 = EXCLUDED.act_75,
                        test_policy = EXCLUDED.test_policy
                    """,
                    (
                        uuid.uuid4(),
                        persisted_id,
                        record["academic_cycle"],
                        row.get("acceptance_rate") or None,
                        row.get("sat_25") or None,
                        row.get("sat_50") or None,
                        row.get("sat_75") or None,
                        row.get("act_25") or None,
                        row.get("act_50") or None,
                        row.get("act_75") or None,
                        row.get("test_policy") or "UNKNOWN",
                    ),
                )
            cursor.execute(
                """
                INSERT INTO college_sources
                    (id, college_id, field_group, field_name, source_type, source_url,
                     academic_cycle, retrieved_at, freshness, confidence)
                SELECT %s, %s, 'IMPORT', 'record', %s, %s, %s, %s, 'CURRENT', 'MEDIUM'
                WHERE NOT EXISTS (
                    SELECT 1 FROM college_sources
                    WHERE college_id = %s AND field_name = 'record' AND source_url = %s
                          AND academic_cycle = %s
                )
                """,
                (
                    uuid.uuid4(),
                    persisted_id,
                    row.get("source_type") or "OFFICIAL",
                    row["source_url"],
                    record["academic_cycle"],
                    now,
                    persisted_id,
                    row["source_url"],
                    record["academic_cycle"],
                ),
            )
    record.update(status="PROMOTED", promoted_at=now.isoformat())
    save_run(record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    import_parser = commands.add_parser("import")
    import_parser.add_argument("source", type=Path)
    import_parser.add_argument("--cycle", required=True)
    for name in ("validate", "diff", "approve", "promote"):
        command = commands.add_parser(name)
        command.add_argument("run_id")
        if name in {"approve", "promote"}:
            command.add_argument("--confirm", required=True)
    args = parser.parse_args()
    if args.command == "import":
        result: object = {"run_id": import_rows(args.source, args.cycle)}
    elif args.command == "validate":
        result = validate(args.run_id)
    elif args.command == "diff":
        result = diff(args.run_id)
    elif args.command == "approve":
        result = approve(args.run_id, args.confirm)
    else:
        result = promote(args.run_id, args.confirm)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
