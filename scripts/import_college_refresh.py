"""Validate and apply the September 2026 college-data refresh layer.

The normalized Batch 1/2 package remains the source of truth for college
identity. This importer deliberately ignores identity fields in the wide refresh
file because four legacy records point at the wrong institution/campus.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from api.admission_engine.config import get_settings
from scripts.import_college_batch import NEED_POLICIES, TEST_POLICIES

TARGET_CYCLE = "2026-27"
EXPECTED_WIDE_ROWS = 200
EXPECTED_DETAIL_ROWS = 12
EXPECTED_SOURCE_ROWS = 242
IDENTITY_EXCEPTIONS = {
    "arizona-state-university",
    "north-carolina-state-university",
    "purdue-university",
    "texas-a-and-m-university",
}
SOURCE_FIELD_NAMES = {
    "ADMISSIONS": "admissions_profile",
    "ADMISSIONS_METRICS": "admissions_metrics",
    "APPLICATION_FEE": "application_fee_usd",
    "COST_OF_ATTENDANCE": "cost_of_attendance",
    "INTERNATIONAL_FINANCIAL_AID": "international_aid_policy",
}
INSTITUTION_TYPES = {
    "PRIVATE NONPROFIT": "PRIVATE_NONPROFIT",
    "PRIVATE_NONPROFIT": "PRIVATE_NONPROFIT",
    "PUBLIC": "PUBLIC",
}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

connect_database = psycopg.connect


class RefreshValidationError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("College refresh validation failed:\n- " + "\n- ".join(errors))
        self.errors = errors


@dataclass(frozen=True)
class CollegeRefresh:
    identities: list[dict[str, Any]]
    wide: list[dict[str, Any]]
    admissions: list[dict[str, Any]]
    financial_aid: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    source_rows_read: int
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RefreshReport:
    files_read: int
    rows_read: int
    valid_rows: int
    rejected_rows: int
    warnings: int
    colleges_updated: int
    policy_rows_updated: int
    admissions_updated: int
    financial_aid_updated: int
    sources_upserted: int
    dry_run: bool


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise RefreshValidationError([f"missing required file: {path}"])
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [dict(row) for row in csv.DictReader(stream)]


def _required(value: str | None, label: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise RefreshValidationError([f"{label}: required"])
    return normalized


def _decimal(
    value: str | None,
    label: str,
    *,
    minimum: Decimal = Decimal(0),
    maximum: Decimal | None = None,
) -> Decimal | None:
    normalized = (value or "").strip()
    if not normalized:
        return None
    try:
        parsed = Decimal(normalized)
    except InvalidOperation as exc:
        raise RefreshValidationError([f"{label}: expected a number"]) from exc
    if not parsed.is_finite() or parsed < minimum or (maximum is not None and parsed > maximum):
        raise RefreshValidationError([f"{label}: outside allowed range"])
    return parsed


def _integer(value: str | None, label: str) -> int | None:
    parsed = _decimal(value, label)
    if parsed is None:
        return None
    if parsed != parsed.to_integral_value():
        raise RefreshValidationError([f"{label}: expected an integer"])
    return int(parsed)


def _boolean(value: str | None, label: str) -> bool | None:
    normalized = (value or "").strip().upper()
    if normalized in {"TRUE", "YES"}:
        return True
    if normalized in {"FALSE", "NO"}:
        return False
    if normalized in {"", "UNKNOWN"}:
        return None
    raise RefreshValidationError([f"{label}: expected true, false, YES, NO, or blank"])


def _boolean_with_status(value: str | None) -> tuple[bool | None, str]:
    normalized = (value or "UNKNOWN").strip().upper() or "UNKNOWN"
    if normalized in {"TRUE", "YES"}:
        return True, "YES"
    if normalized in {"FALSE", "NO"}:
        return False, "NO"
    return None, normalized


def _enum(value: str | None, allowed: set[str], label: str) -> str:
    normalized = _required(value, label).upper()
    if normalized not in allowed:
        raise RefreshValidationError([f"{label}: invalid value {normalized}"])
    return normalized


def _url(value: str | None, label: str) -> str:
    normalized = _required(value, label)
    parsed = urlparse(normalized)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise RefreshValidationError([f"{label}: invalid HTTP/HTTPS URL"])
    return normalized


def _date(value: str | None, label: str) -> datetime:
    normalized = _required(value, label)
    try:
        return datetime.fromisoformat(normalized).replace(tzinfo=UTC)
    except ValueError as exc:
        raise RefreshValidationError([f"{label}: invalid ISO date"]) from exc


def _unique(rows: list[dict[str, str]], key: str, label: str) -> None:
    values = [(row.get(key) or "").strip() for row in rows]
    duplicates = sorted({value for value in values if value and values.count(value) > 1})
    if duplicates:
        raise RefreshValidationError([f"{label}: duplicate {key}: {', '.join(duplicates[:5])}"])


def _score_values(row: dict[str, str], label: str) -> dict[str, Decimal | None]:
    values = {
        key: _decimal(row.get(key), f"{label} {key}", minimum=Decimal(400), maximum=Decimal(1600))
        for key in ("sat_25", "sat_50", "sat_75")
    }
    values.update(
        {
            key: _decimal(row.get(key), f"{label} {key}", minimum=Decimal(1), maximum=Decimal(36))
            for key in ("act_25", "act_50", "act_75")
        }
    )
    for prefix in ("sat", "act"):
        ordered = [values[f"{prefix}_{percentile}"] for percentile in (25, 50, 75)]
        present = [value for value in ordered if value is not None]
        if present != sorted(present):
            raise RefreshValidationError([f"{label}: {prefix.upper()} percentile order"])
    return values


def _platforms(value: str | None, label: str) -> list[str]:
    platforms = list(
        dict.fromkeys(part.strip().upper() for part in (value or "").split(";") if part.strip())
    )
    if not platforms:
        raise RefreshValidationError([f"{label}: at least one platform is required"])
    return platforms


def parse_refresh(root: Path, *, seed_root: Path = Path("data/data_v2/seed")) -> CollegeRefresh:
    errors: list[str] = []
    warnings: list[str] = []
    raw_canonical = _read_csv(seed_root / "colleges.csv")
    canonical = {(row.get("slug") or "").strip(): row for row in raw_canonical}
    if len(canonical) != EXPECTED_WIDE_ROWS:
        errors.append(f"canonical colleges.csv: expected 200 rows, found {len(canonical)}")

    raw_identities = _read_csv(root / "colleges_UPDATED.csv")
    raw_wide = _read_csv(root / "evalio_top200_us_colleges_enriched_UPDATED.csv")
    raw_admissions = _read_csv(root / "admissions_UPDATED.csv")
    raw_aid = _read_csv(root / "financial_aid_UPDATED.csv")
    raw_sources = _read_csv(root / "update_sources.csv")
    fee_status_by_slug: dict[str, str] = {}
    for source_row in raw_sources:
        if (source_row.get("field_group") or "").strip().upper() != "APPLICATION_FEE":
            continue
        notes = (source_row.get("notes") or "").strip()
        if notes.upper().startswith("FEE STATUS:"):
            fee_status_by_slug[(source_row.get("slug") or "").strip()] = notes.split(":", 1)[
                1
            ].strip()

    expected_counts = (
        ("colleges_UPDATED.csv", raw_identities, EXPECTED_DETAIL_ROWS),
        ("admissions_UPDATED.csv", raw_admissions, EXPECTED_DETAIL_ROWS),
        ("financial_aid_UPDATED.csv", raw_aid, EXPECTED_DETAIL_ROWS),
        ("wide refresh", raw_wide, EXPECTED_WIDE_ROWS),
        ("update_sources.csv", raw_sources, EXPECTED_SOURCE_ROWS),
    )
    for label, rows, expected in expected_counts:
        if len(rows) != expected:
            errors.append(f"{label}: expected {expected} rows, found {len(rows)}")
    for label, rows, key in (
        ("colleges_UPDATED.csv", raw_identities, "slug"),
        ("admissions_UPDATED.csv", raw_admissions, "slug"),
        ("financial_aid_UPDATED.csv", raw_aid, "slug"),
        ("wide refresh", raw_wide, "school_id"),
    ):
        try:
            _unique(rows, key, label)
        except RefreshValidationError as exc:
            errors.extend(exc.errors)

    identities: list[dict[str, Any]] = []
    for line, row in enumerate(raw_identities, 2):
        label = f"colleges_UPDATED.csv line {line}"
        try:
            slug = _required(row.get("slug"), f"{label} slug")
            reference = canonical.get(slug)
            if reference is None:
                raise RefreshValidationError([f"{label}: unknown slug {slug}"])
            name = _required(row.get("name"), f"{label} name")
            ipeds_id = _required(row.get("ipeds_id"), f"{label} ipeds_id")
            if ipeds_id != reference.get("ipeds_id"):
                raise RefreshValidationError([f"{label}: identity differs from canonical seed"])
            if name != reference.get("display_name"):
                warnings.append(
                    f"ignored display-name alias for {slug}; canonical Batch 1 name wins"
                )
            institution_type = INSTITUTION_TYPES.get(
                _required(row.get("institution_type"), f"{label} institution_type").upper()
            )
            if institution_type != reference.get("institution_type"):
                raise RefreshValidationError([f"{label}: institution type differs from canonical seed"])
            identities.append(
                {
                    "slug": slug,
                    "official_website": _url(row.get("official_website"), f"{label} website"),
                    "common_app_member": _boolean(row.get("common_app_member"), f"{label} common app"),
                    "active": _boolean(row.get("active"), f"{label} active"),
                }
            )
        except RefreshValidationError as exc:
            errors.extend(exc.errors)

    wide: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    identity_mismatches: set[str] = set()
    for line, row in enumerate(raw_wide, 2):
        label = f"wide refresh line {line}"
        try:
            slug = _required(row.get("school_id"), f"{label} school_id")
            if not SLUG_PATTERN.fullmatch(slug) or slug not in canonical:
                raise RefreshValidationError([f"{label}: unknown or invalid slug {slug}"])
            school_name = _required(row.get("school_name"), f"{label} school_name")
            if school_name in seen_names:
                raise RefreshValidationError([f"{label}: duplicate school_name {school_name}"])
            seen_names.add(school_name)
            if school_name != canonical[slug].get("display_name"):
                identity_mismatches.add(slug)
            scores = _score_values(row, label)
            acceptance = _decimal(row.get("acceptance_rate"), f"{label} acceptance_rate", maximum=Decimal(100))
            fee = _decimal(row.get("app_fee_usd"), f"{label} app_fee_usd")
            fee_status = fee_status_by_slug.get(slug)
            if fee is not None and not fee_status:
                raise RefreshValidationError([f"{label}: fee has no provenance status"])
            tuition = _decimal(row.get("tuition_usd"), f"{label} tuition_usd")
            coa = _decimal(row.get("estimated_cost_of_attendance_usd"), f"{label} coa")
            if tuition is not None and coa is not None and coa < tuition:
                raise RefreshValidationError([f"{label}: COA below tuition"])
            platforms = _platforms(row.get("application_platforms"), f"{label} platforms")
            primary = _required(row.get("application_platform_primary"), f"{label} primary").upper()
            if primary not in platforms:
                raise RefreshValidationError([f"{label}: primary platform absent from list"])
            need_aid, need_aid_status = _boolean_with_status(row.get("international_need_based_aid"))
            full_need, full_need_status = _boolean_with_status(
                row.get("meets_full_demonstrated_need_international")
            )
            wide.append(
                {
                    "slug": slug,
                    "application_platform_primary": primary,
                    "application_platforms": platforms,
                    "test_policy": _enum(row.get("test_policy_2026_27"), TEST_POLICIES, f"{label} test policy"),
                    "test_policy_status": _required(row.get("test_policy_status"), f"{label} test status"),
                    "application_fee_usd": fee,
                    "application_fee_status": fee_status,
                    "need_policy": _enum(row.get("international_aid_policy"), NEED_POLICIES, f"{label} need policy"),
                    "aid_policy_status": _required(row.get("aid_policy_status"), f"{label} aid status"),
                    "international_need_based_aid": need_aid,
                    "international_need_based_aid_status": need_aid_status,
                    "meets_full_demonstrated_need": full_need,
                    "meets_full_demonstrated_need_status": full_need_status,
                    "acceptance_rate": acceptance,
                    "tuition": tuition,
                    "estimated_cost_of_attendance": coa,
                    **scores,
                }
            )
        except RefreshValidationError as exc:
            errors.extend(exc.errors)
    if identity_mismatches:
        if identity_mismatches != IDENTITY_EXCEPTIONS:
            errors.append(
                "wide refresh: unexpected identity mismatches: "
                + ", ".join(sorted(identity_mismatches ^ IDENTITY_EXCEPTIONS))
            )
        warnings.append(
            "ignored four known legacy identity mismatches; canonical Batch 1 identities win"
        )

    admissions: list[dict[str, Any]] = []
    detail_slugs = {(row.get("slug") or "").strip() for row in raw_identities}
    for line, row in enumerate(raw_admissions, 2):
        label = f"admissions_UPDATED.csv line {line}"
        try:
            slug = _required(row.get("slug"), f"{label} slug")
            if slug not in detail_slugs:
                raise RefreshValidationError([f"{label}: slug not present in colleges_UPDATED.csv"])
            applicants = _integer(row.get("applicants_total"), f"{label} applicants")
            admits = _integer(row.get("admits_total"), f"{label} admits")
            enrolled = _integer(row.get("enrolled_total"), f"{label} enrolled")
            acceptance = _decimal(row.get("acceptance_rate"), f"{label} acceptance", maximum=Decimal(100))
            if applicants is not None and admits is not None and admits > applicants:
                raise RefreshValidationError([f"{label}: admits exceed applicants"])
            if admits is not None and enrolled is not None and enrolled > admits:
                raise RefreshValidationError([f"{label}: enrolled exceed admits"])
            if applicants and admits is not None and acceptance is not None:
                calculated = Decimal(admits * 100) / Decimal(applicants)
                if abs(calculated - acceptance) > Decimal("0.01"):
                    raise RefreshValidationError([f"{label}: acceptance rate conflicts with counts"])
            admissions.append(
                {
                    "slug": slug,
                    "source_cycle": _required(row.get("academic_cycle"), f"{label} cycle"),
                    "applicants_total": applicants,
                    "admits_total": admits,
                    "enrolled_total": enrolled,
                    "acceptance_rate": acceptance / Decimal(100) if acceptance is not None else None,
                    "international_applicants": _integer(row.get("international_applicants"), f"{label} international applicants"),
                    "international_admits": _integer(row.get("international_admits"), f"{label} international admits"),
                    "test_policy": _enum(row.get("test_policy"), TEST_POLICIES, f"{label} test policy"),
                    **_score_values(row, label),
                }
            )
        except RefreshValidationError as exc:
            errors.extend(exc.errors)

    financial_aid: list[dict[str, Any]] = []
    for line, row in enumerate(raw_aid, 2):
        label = f"financial_aid_UPDATED.csv line {line}"
        try:
            slug = _required(row.get("slug"), f"{label} slug")
            if slug not in detail_slugs:
                raise RefreshValidationError([f"{label}: slug not present in colleges_UPDATED.csv"])
            cycle = _required(row.get("academic_cycle"), f"{label} cycle")
            if cycle != TARGET_CYCLE:
                raise RefreshValidationError([f"{label}: expected cycle {TARGET_CYCLE}"])
            tuition = _decimal(row.get("tuition"), f"{label} tuition")
            coa = _decimal(row.get("estimated_cost_of_attendance"), f"{label} COA")
            if tuition is not None and coa is not None and coa < tuition:
                raise RefreshValidationError([f"{label}: COA below tuition"])
            need_aid, need_aid_status = _boolean_with_status(row.get("international_need_based_aid"))
            full_need, full_need_status = _boolean_with_status(row.get("meets_full_demonstrated_need"))
            financial_aid.append(
                {
                    "slug": slug,
                    "source_cycle": cycle,
                    "need_policy": _enum(row.get("need_policy"), NEED_POLICIES, f"{label} need policy"),
                    "international_need_based_aid": need_aid,
                    "international_need_based_aid_status": need_aid_status,
                    "meets_full_demonstrated_need": full_need,
                    "meets_full_demonstrated_need_status": full_need_status,
                    "css_profile_required": _boolean(row.get("css_profile_required"), f"{label} CSS Profile"),
                    "estimated_cost_of_attendance": coa,
                    "tuition": tuition,
                    "room_board": _decimal(row.get("room_board"), f"{label} room_board"),
                    "books_personal": _decimal(row.get("books_personal"), f"{label} books_personal"),
                    "currency": _required(row.get("currency"), f"{label} currency").upper(),
                    "notes": (row.get("notes") or "").strip() or None,
                }
            )
        except RefreshValidationError as exc:
            errors.extend(exc.errors)

    sources_by_key: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    duplicate_sources = 0
    for line, row in enumerate(raw_sources, 2):
        label = f"update_sources.csv line {line}"
        try:
            slug = _required(row.get("slug"), f"{label} slug")
            if slug not in canonical:
                raise RefreshValidationError([f"{label}: unknown slug {slug}"])
            group = _required(row.get("field_group"), f"{label} field group").upper()
            field_name = SOURCE_FIELD_NAMES.get(group)
            if field_name is None:
                raise RefreshValidationError([f"{label}: unsupported field group {group}"])
            source_type = _required(row.get("source_type"), f"{label} source type").upper()
            source_url = _url(row.get("source_url"), f"{label} source URL")
            cycle = _required(row.get("academic_cycle"), f"{label} cycle")
            verified_at = _date(row.get("verified_at"), f"{label} verified_at")
            parsed = {
                "slug": slug,
                "field_group": group,
                "field_name": field_name,
                "source_type": source_type,
                "source_url": source_url,
                "source_cycle": cycle,
                "retrieved_at": verified_at,
                "verified_at": verified_at,
                "freshness": (
                    "CURRENT"
                    if cycle in {TARGET_CYCLE, "CURRENT_POLICY"}
                    else "CURRENT_OR_LATEST_AVAILABLE"
                ),
                "confidence": "MEDIUM" if source_type == "SOURCE_LINKED_CDS_ARCHIVE" else "HIGH",
                "notes": (row.get("notes") or "").strip() or None,
            }
            key = (slug, group, field_name, source_url, cycle)
            if key in sources_by_key:
                duplicate_sources += 1
            else:
                sources_by_key[key] = parsed
        except RefreshValidationError as exc:
            errors.extend(exc.errors)
    if duplicate_sources:
        warnings.append(f"deduplicated {duplicate_sources} repeated source rows")

    if errors:
        raise RefreshValidationError(errors)
    return CollegeRefresh(
        identities=identities,
        wide=wide,
        admissions=admissions,
        financial_aid=financial_aid,
        sources=list(sources_by_key.values()),
        source_rows_read=len(raw_sources),
        warnings=warnings,
    )


def _database_url() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def import_refresh(
    refresh: CollegeRefresh,
    *,
    environment: str | None = None,
    dry_run: bool = False,
    database_url: str | None = None,
) -> RefreshReport:
    report = RefreshReport(
        files_read=5,
        rows_read=(
            len(refresh.identities)
            + len(refresh.wide)
            + len(refresh.admissions)
            + len(refresh.financial_aid)
            + refresh.source_rows_read
        ),
        valid_rows=(
            len(refresh.identities)
            + len(refresh.wide)
            + len(refresh.admissions)
            + len(refresh.financial_aid)
            + refresh.source_rows_read
        ),
        rejected_rows=0,
        warnings=len(refresh.warnings),
        colleges_updated=len(refresh.identities),
        policy_rows_updated=len(refresh.wide),
        admissions_updated=len(refresh.admissions),
        financial_aid_updated=len(refresh.financial_aid),
        sources_upserted=len(refresh.sources),
        dry_run=dry_run,
    )
    if dry_run:
        return report
    normalized_environment = (environment or "").strip().lower()
    if normalized_environment not in {"local", "staging"}:
        raise ValueError("database writes require explicit --environment local or staging")
    if os.getenv("APP_ENV", "").strip().lower() == "production":
        raise ValueError("refusing college refresh import while APP_ENV=production")

    with connect_database(database_url or _database_url()) as connection, connection.cursor() as cursor:
        slugs = [row["slug"] for row in refresh.wide]
        cursor.execute("SELECT slug, id FROM colleges WHERE slug = ANY(%s)", (slugs,))
        college_ids = dict(cursor.fetchall())
        missing = sorted(set(slugs) - set(college_ids))
        if missing:
            raise ValueError(
                "refresh requires normalized Batch 1 first; missing colleges: "
                + ", ".join(missing[:10])
            )
        for table in ("college_admissions", "college_financial_aid"):
            cursor.execute(
                sql.SQL(
                    """
                SELECT c.slug FROM colleges c
                JOIN {} d ON d.college_id=c.id
                WHERE c.slug=ANY(%s) AND d.academic_cycle=%s
                """
                ).format(sql.Identifier(table)),
                (slugs, TARGET_CYCLE),
            )
            present = {row[0] for row in cursor.fetchall()}
            missing_details = sorted(set(slugs) - present)
            if missing_details:
                raise ValueError(
                    f"refresh requires {table} Batch 1 rows first; missing: "
                    + ", ".join(missing_details[:10])
                )
        for row in refresh.identities:
            cursor.execute(
                """
                UPDATE colleges SET official_website=%s, common_app_member=%s, active=%s,
                    updated_at=now() WHERE id=%s
                """,
                (
                    row["official_website"], row["common_app_member"], row["active"],
                    college_ids[row["slug"]],
                ),
            )
        for row in refresh.wide:
            college_id = college_ids[row["slug"]]
            cursor.execute(
                """
                UPDATE colleges SET application_platform_primary=%s, application_platforms=%s,
                    updated_at=now() WHERE id=%s
                """,
                (row["application_platform_primary"], Jsonb(row["application_platforms"]), college_id),
            )
            cursor.execute(
                """
                UPDATE college_admissions SET test_policy=%s, test_policy_status=%s,
                    application_fee_usd=COALESCE(%s, application_fee_usd),
                    application_fee_status=CASE WHEN %s IS NULL
                        THEN application_fee_status ELSE %s END, updated_at=now()
                WHERE college_id=%s AND academic_cycle=%s
                """,
                (
                    row["test_policy"], row["test_policy_status"], row["application_fee_usd"],
                    row["application_fee_usd"], row["application_fee_status"],
                    college_id, TARGET_CYCLE,
                ),
            )
            cursor.execute(
                """
                UPDATE college_financial_aid SET need_policy=%s, aid_policy_status=%s,
                    international_need_based_aid=%s,
                    international_need_based_aid_status=%s,
                    meets_full_demonstrated_need=%s,
                    meets_full_demonstrated_need_status=%s, updated_at=now()
                WHERE college_id=%s AND academic_cycle=%s
                """,
                (
                    row["need_policy"], row["aid_policy_status"],
                    row["international_need_based_aid"],
                    row["international_need_based_aid_status"],
                    row["meets_full_demonstrated_need"],
                    row["meets_full_demonstrated_need_status"], college_id, TARGET_CYCLE,
                ),
            )
        for row in refresh.admissions:
            cursor.execute(
                """
                UPDATE college_admissions SET source_cycle=%s, applicants_total=%s,
                    admits_total=%s, enrolled_total=%s, acceptance_rate=%s,
                    international_applicants=%s, international_admits=%s,
                    sat_25=%s, sat_50=%s, sat_75=%s, act_25=%s, act_50=%s, act_75=%s,
                    test_policy=%s, updated_at=now()
                WHERE college_id=%s AND academic_cycle=%s
                """,
                (
                    row["source_cycle"], row["applicants_total"], row["admits_total"],
                    row["enrolled_total"], row["acceptance_rate"],
                    row["international_applicants"], row["international_admits"],
                    row["sat_25"], row["sat_50"], row["sat_75"], row["act_25"],
                    row["act_50"], row["act_75"], row["test_policy"],
                    college_ids[row["slug"]], TARGET_CYCLE,
                ),
            )
        for row in refresh.financial_aid:
            cursor.execute(
                """
                UPDATE college_financial_aid SET source_cycle=%s, need_policy=%s,
                    international_need_based_aid=%s,
                    international_need_based_aid_status=%s,
                    meets_full_demonstrated_need=%s,
                    meets_full_demonstrated_need_status=%s, css_profile_required=%s,
                    estimated_cost_of_attendance=%s, tuition=%s, room_board=%s,
                    books_personal=%s, currency=%s, notes=%s, updated_at=now()
                WHERE college_id=%s AND academic_cycle=%s
                """,
                (
                    row["source_cycle"], row["need_policy"],
                    row["international_need_based_aid"],
                    row["international_need_based_aid_status"],
                    row["meets_full_demonstrated_need"],
                    row["meets_full_demonstrated_need_status"],
                    row["css_profile_required"], row["estimated_cost_of_attendance"],
                    row["tuition"], row["room_board"], row["books_personal"],
                    row["currency"], row["notes"], college_ids[row["slug"]], TARGET_CYCLE,
                ),
            )
        for row in refresh.sources:
            cursor.execute(
                """
                INSERT INTO college_sources
                    (id,college_id,field_group,field_name,source_type,source_url,
                     academic_cycle,retrieved_at,verified_at,freshness,confidence,notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (college_id,field_group,field_name,source_url,academic_cycle)
                DO UPDATE SET source_type=EXCLUDED.source_type,
                    retrieved_at=EXCLUDED.retrieved_at, verified_at=EXCLUDED.verified_at,
                    freshness=EXCLUDED.freshness, confidence=EXCLUDED.confidence,
                    notes=EXCLUDED.notes
                """,
                (
                    uuid.uuid4(), college_ids[row["slug"]], row["field_group"],
                    row["field_name"], row["source_type"], row["source_url"],
                    row["source_cycle"], row["retrieved_at"], row["verified_at"],
                    row["freshness"], row["confidence"], row["notes"],
                ),
            )
    return report


def _print_report(report: RefreshReport, warnings: list[str]) -> None:
    for name in report.__dataclass_fields__:
        print(f"{name.replace('_', ' ')}: {getattr(report, name)}")
    for warning in warnings:
        print(f"  - {warning}")
    if report.dry_run:
        print("dry run: no database connection opened; no rows written")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--seed-root", type=Path, default=Path("data/data_v2/seed"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--environment", choices=("local", "staging"))
    args = parser.parse_args()
    refresh = parse_refresh(args.directory, seed_root=args.seed_root)
    report = import_refresh(refresh, environment=args.environment, dry_run=args.dry_run)
    _print_report(report, refresh.warnings)


if __name__ == "__main__":
    main()
