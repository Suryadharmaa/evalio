"""Validate and import normalized Evalio college research batches.

Batch 1 is the identity/admissions/cost baseline. Batch 2A is applied afterward
as a field-level enrichment layer. The importer is never called by web routes.
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
from psycopg.types.json import Jsonb

from api.admission_engine.config import get_settings

ACADEMIC_CYCLE = "2026-27"
EXPECTED_COLLEGES = 200
EXPECTED_ENRICHMENT_ROWS = 50
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEST_POLICIES = {
    "REQUIRED", "OPTIONAL", "FLEXIBLE", "BLIND", "NOT_ACCEPTED",
    "PROGRAM_DEPENDENT", "OPTIONAL_FOR_INTL_OUTSIDE_US",
    "OPTIONAL_WITH_PROGRAM_EXCEPTIONS", "UNKNOWN",
}
NEED_POLICIES = {
    "NEED_BLIND", "NEED_AWARE", "NO_NEED_BASED_AID", "LIMITED",
    "LIMITED_NEED_BASED", "MERIT_FOCUSED_LIMITED", "NEED_AWARE_OR_SELECTIVE",
    "NO_NEED_BASED_AID_OR_VERY_LIMITED", "UNKNOWN",
    "MERIT_AND_LIMITED_GRANTS", "MERIT_FOCUSED", "MERIT_ONLY",
    "MERIT_ONLY_LIMITED", "MERIT_ONLY_OR_LIMITED",
    "MERIT_ONLY_WITH_CANADIAN_EXCEPTION", "MERIT_OR_LIMITED",
    "MERIT_SCHOLARSHIPS", "NEED_AWARE_LIMITED", "NEED_AWARE_NO_NEED_AID",
    "NEED_BASED_AVAILABLE", "NEED_BLIND_ADMISSION_NO_NEED_AID",
    "NO_SCHOLARSHIPS_FOR_INTL_UNDERGRAD", "SCHOLARSHIP_AVAILABLE",
}
INSTITUTION_TYPES = {"PUBLIC", "PRIVATE_NONPROFIT", "PRIVATE_FOR_PROFIT", "UNKNOWN"}
CONFIDENCE_VALUES = {"HIGH", "MEDIUM", "LOW"}
FRESHNESS_VALUES = {"CURRENT", "CURRENT_OR_LATEST_AVAILABLE", "REVIEW_SOON", "STALE", "UNKNOWN"}
REQUIREMENT_FIELDS = {
    "fall_2027_deadlines": "APPLICATION_DEADLINES",
    "fee_waiver": "APPLICATION_FEE_WAIVER",
    "test_policy_note": "TEST_POLICY_NOTE",
    "english_requirement": "ENGLISH_REQUIREMENT",
    "english_tests_minimums": "ENGLISH_TEST_MINIMUMS",
    "teacher_recommendations": "TEACHER_RECOMMENDATIONS",
    "counselor_recommendation_or_report": "COUNSELOR_RECOMMENDATION_OR_REPORT",
    "midyear_report": "MIDYEAR_REPORT",
    "writing_or_supplement": "WRITING_OR_SUPPLEMENT",
    "portfolio": "PORTFOLIO",
    "interview": "INTERVIEW",
}

connect_database = psycopg.connect


class BatchValidationError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("College batch validation failed:\n- " + "\n- ".join(errors))
        self.errors = errors


@dataclass(frozen=True)
class CollegeBatch:
    colleges: list[dict[str, Any]]
    admissions: list[dict[str, Any]]
    financial_aid: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    media: list[dict[str, Any]]
    requirements: list[dict[str, Any]]
    enrichment: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)


@dataclass
class ImportReport:
    files_read: int = 0
    rows_read: int = 0
    valid_rows: int = 0
    rejected_rows: int = 0
    warnings: int = 0
    colleges_upserted: int = 0
    admissions_upserted: int = 0
    financial_aid_upserted: int = 0
    requirements_upserted: int = 0
    sources_upserted: int = 0
    media_upserted: int = 0
    dry_run: bool = False


def _read_csv(path: Path, *, preamble_lines: int = 0) -> list[dict[str, str]]:
    if not path.is_file():
        raise BatchValidationError([f"missing required file: {path}"])
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for _ in range(preamble_lines):
            next(stream, None)
        return [dict(row) for row in csv.DictReader(stream)]


def _required(value: str | None, label: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise BatchValidationError([f"{label}: required"])
    return normalized


def _enum(value: str | None, allowed: set[str], label: str) -> str:
    normalized = _required(value, label).upper()
    if normalized not in allowed:
        raise BatchValidationError([f"{label}: invalid value {normalized}"])
    return normalized


def _url(value: str | None, label: str, *, required: bool = False) -> str | None:
    normalized = (value or "").strip()
    if not normalized:
        if required:
            raise BatchValidationError([f"{label}: required"])
        return None
    parsed = urlparse(normalized)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise BatchValidationError([f"{label}: invalid HTTP/HTTPS URL"])
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
        raise BatchValidationError([f"{label}: expected a number"]) from exc
    if not parsed.is_finite() or parsed < minimum or (maximum is not None and parsed > maximum):
        raise BatchValidationError([f"{label}: outside allowed range"])
    return parsed


def _integer(value: str | None, label: str) -> int | None:
    parsed = _decimal(value, label)
    if parsed is None:
        return None
    if parsed != parsed.to_integral_value():
        raise BatchValidationError([f"{label}: expected an integer"])
    return int(parsed)


def parse_nullable_boolean(value: str | None, label: str) -> bool | None:
    normalized = (value or "").strip().upper()
    if normalized in {"YES", "TRUE"}:
        return True
    if normalized in {"NO", "FALSE"}:
        return False
    if normalized in {"", "UNKNOWN", "PENDING"}:
        return None
    raise BatchValidationError([f"{label}: expected YES, NO, UNKNOWN, or blank"])


def _nullable_boolean_with_status(value: str | None) -> tuple[bool | None, str]:
    normalized = (value or "UNKNOWN").strip().upper() or "UNKNOWN"
    if normalized == "YES":
        return True, normalized
    if normalized == "NO":
        return False, normalized
    return None, normalized


def _platforms(value: str | None, label: str) -> list[str]:
    result = list(dict.fromkeys(part.strip().upper() for part in (value or "").split(";") if part.strip()))
    if not result:
        raise BatchValidationError([f"{label}: at least one platform is required"])
    return result


def _iso_datetime(value: str | None, label: str) -> datetime:
    normalized = _required(value, label).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise BatchValidationError([f"{label}: invalid ISO date/time"]) from exc
    return parsed.replace(tzinfo=parsed.tzinfo or UTC)


def _requirement_status(value: str) -> str:
    upper = value.upper()
    return "PENDING" if "PENDING" in upper or upper == "UNKNOWN" else "DOCUMENTED"


def _validate_unique(rows: list[dict[str, str]], field_name: str, label: str) -> None:
    values = [(row.get(field_name) or "").strip() for row in rows]
    duplicates = sorted({value for value in values if value and values.count(value) > 1})
    if duplicates:
        raise BatchValidationError([f"{label}: duplicate {field_name}: {', '.join(duplicates[:5])}"])


def parse_batch(root: Path) -> CollegeBatch:
    errors: list[str] = []
    warnings: list[str] = []
    raw_colleges = _read_csv(root / "colleges.csv")
    raw_admissions = _read_csv(root / "admissions.csv")
    raw_aid = _read_csv(root / "financial_aid.csv")
    raw_sources = _read_csv(root / "sources.csv")
    raw_media = _read_csv(root / "college_media.csv")
    if len(raw_colleges) != EXPECTED_COLLEGES:
        errors.append(f"colleges.csv: expected 200 rows, found {len(raw_colleges)}")
    try:
        _validate_unique(raw_colleges, "slug", "colleges.csv")
        _validate_unique(raw_colleges, "ipeds_id", "colleges.csv")
    except BatchValidationError as exc:
        errors.extend(exc.errors)
    slugs = {(row.get("slug") or "").strip() for row in raw_colleges}
    for name, rows in (("admissions.csv", raw_admissions), ("financial_aid.csv", raw_aid)):
        if len(rows) != EXPECTED_COLLEGES:
            errors.append(f"{name}: expected 200 rows, found {len(rows)}")
        unknown = sorted({(row.get("slug") or "").strip() for row in rows} - slugs)
        missing = sorted(slugs - {(row.get("slug") or "").strip() for row in rows})
        if unknown or missing:
            errors.append(f"{name}: slug coverage mismatch")

    colleges: list[dict[str, Any]] = []
    for index, row in enumerate(raw_colleges, 2):
        try:
            slug = _required(row.get("slug"), f"colleges.csv line {index} slug")
            if not SLUG_PATTERN.fullmatch(slug):
                raise BatchValidationError([f"colleges.csv line {index}: invalid slug"])
            platforms = _platforms(row.get("application_platforms"), f"colleges.csv line {index}")
            primary = _required(row.get("application_platform_primary"), f"colleges.csv line {index}").upper()
            if primary not in platforms:
                raise BatchValidationError([f"colleges.csv line {index}: primary platform absent from list"])
            display_name = _required(row.get("display_name"), f"colleges.csv line {index} display_name")
            colleges.append({
                "slug": slug,
                "name": display_name,
                "official_name": _required(row.get("official_name"), f"colleges.csv line {index} official_name"),
                "normalized_name": " ".join(display_name.casefold().split()),
                "ipeds_id": _required(row.get("ipeds_id"), f"colleges.csv line {index} ipeds_id"),
                "country_code": _required(row.get("country_code"), f"colleges.csv line {index} country_code").upper(),
                "state_region": (row.get("state_region") or "").strip() or None,
                "city": (row.get("city") or "").strip() or None,
                "institution_type": _enum(row.get("institution_type"), INSTITUTION_TYPES, f"colleges.csv line {index} institution_type"),
                "selection_group": (row.get("selection_group") or "").strip() or None,
                "application_platform_primary": primary,
                "application_platforms": platforms,
                "official_website": _url(row.get("official_website"), f"colleges.csv line {index} official_website"),
                "common_app_member": parse_nullable_boolean(row.get("common_app_member"), f"colleges.csv line {index} common_app_member"),
                "active": parse_nullable_boolean(row.get("active"), f"colleges.csv line {index} active"),
                "identity_confidence": _enum(row.get("identity_confidence"), CONFIDENCE_VALUES, f"colleges.csv line {index} identity_confidence"),
            })
        except BatchValidationError as exc:
            errors.extend(exc.errors)

    admissions: list[dict[str, Any]] = []
    for index, row in enumerate(raw_admissions, 2):
        try:
            values = {
                key: _decimal(row.get(key), f"admissions.csv line {index} {key}", minimum=Decimal(400), maximum=Decimal(1600))
                for key in ("sat_25", "sat_50", "sat_75")
            }
            values.update({
                key: _decimal(row.get(key), f"admissions.csv line {index} {key}", minimum=Decimal(1), maximum=Decimal(36))
                for key in ("act_25", "act_50", "act_75")
            })
            sat = [values[key] for key in ("sat_25", "sat_50", "sat_75")]
            act = [values[key] for key in ("act_25", "act_50", "act_75")]
            if all(value is not None for value in sat) and sat != sorted(sat):
                raise BatchValidationError([f"admissions.csv line {index}: SAT percentile order"])
            if all(value is not None for value in act) and act != sorted(act):
                raise BatchValidationError([f"admissions.csv line {index}: ACT percentile order"])
            acceptance_pct = _decimal(row.get("acceptance_rate_pct"), f"admissions.csv line {index} acceptance_rate_pct", maximum=Decimal(100))
            admissions.append({
                "slug": _required(row.get("slug"), f"admissions.csv line {index} slug"),
                "source_cycle": _required(row.get("source_cycle"), f"admissions.csv line {index} source_cycle"),
                "applicants_total": _integer(row.get("applicants_total"), f"admissions.csv line {index} applicants_total"),
                "admits_total": _integer(row.get("admits_total"), f"admissions.csv line {index} admits_total"),
                "enrolled_total": _integer(row.get("enrolled_total"), f"admissions.csv line {index} enrolled_total"),
                "acceptance_rate": acceptance_pct / Decimal(100) if acceptance_pct is not None else None,
                "yield_rate_pct": _decimal(row.get("yield_rate_pct"), f"admissions.csv line {index} yield_rate_pct", maximum=Decimal(100)),
                **values,
                "test_policy": _enum(row.get("test_policy_2026_27"), TEST_POLICIES, f"admissions.csv line {index} test_policy"),
                "test_policy_status": _required(row.get("test_policy_status"), f"admissions.csv line {index} test_policy_status"),
                "application_fee_usd": _decimal(row.get("application_fee_usd"), f"admissions.csv line {index} application_fee_usd"),
            })
        except BatchValidationError as exc:
            errors.extend(exc.errors)

    financial_aid: list[dict[str, Any]] = []
    for index, row in enumerate(raw_aid, 2):
        try:
            tuition = _decimal(row.get("tuition_usd"), f"financial_aid.csv line {index} tuition")
            coa = _decimal(row.get("estimated_cost_of_attendance_usd"), f"financial_aid.csv line {index} coa")
            if tuition is not None and coa is not None and coa < tuition:
                raise BatchValidationError([f"financial_aid.csv line {index}: COA below tuition"])
            financial_aid.append({
                "slug": _required(row.get("slug"), f"financial_aid.csv line {index} slug"),
                "source_cycle": _required(row.get("source_cycle"), f"financial_aid.csv line {index} source_cycle"),
                "need_policy": _enum(row.get("international_aid_policy"), NEED_POLICIES, f"financial_aid.csv line {index} aid policy"),
                "aid_policy_status": _required(row.get("aid_policy_status"), f"financial_aid.csv line {index} aid status"),
                "international_need_based_aid": parse_nullable_boolean(row.get("international_need_based_aid"), f"financial_aid.csv line {index} need aid"),
                "international_need_based_aid_status": _required(row.get("international_need_based_aid"), f"financial_aid.csv line {index} need aid status").upper(),
                "meets_full_demonstrated_need": parse_nullable_boolean(row.get("meets_full_demonstrated_need_international"), f"financial_aid.csv line {index} full need"),
                "meets_full_demonstrated_need_status": _required(row.get("meets_full_demonstrated_need_international"), f"financial_aid.csv line {index} full need status").upper(),
                "tuition": tuition,
                "mandatory_fees": _decimal(row.get("mandatory_fees_usd"), f"financial_aid.csv line {index} mandatory fees"),
                "room_board": _decimal(row.get("room_board_usd"), f"financial_aid.csv line {index} room board"),
                "estimated_cost_of_attendance": coa,
                "cost_basis": _required(row.get("cost_basis"), f"financial_aid.csv line {index} cost basis"),
                "currency": _required(row.get("currency"), f"financial_aid.csv line {index} currency").upper(),
                "notes": (row.get("notes") or "").strip() or None,
            })
        except BatchValidationError as exc:
            errors.extend(exc.errors)

    sources: list[dict[str, Any]] = []
    for index, row in enumerate(raw_sources, 2):
        try:
            sources.append({
                "slug": _required(row.get("slug"), f"sources.csv line {index} slug"),
                "field_group": _required(row.get("field_group"), f"sources.csv line {index} field_group"),
                "field_name": _required(row.get("field_name"), f"sources.csv line {index} field_name"),
                "source_type": _required(row.get("source_type"), f"sources.csv line {index} source_type"),
                "source_url": _url(row.get("source_url"), f"sources.csv line {index} source_url", required=True),
                "source_cycle": _required(row.get("source_cycle"), f"sources.csv line {index} source_cycle"),
                "retrieved_at": _iso_datetime(row.get("retrieved_at"), f"sources.csv line {index} retrieved_at"),
                "verified_at": _iso_datetime(row.get("verified_at"), f"sources.csv line {index} verified_at") if (row.get("verified_at") or "").strip() else None,
                "freshness": _enum(row.get("freshness"), FRESHNESS_VALUES, f"sources.csv line {index} freshness"),
                "confidence": _enum(row.get("confidence"), CONFIDENCE_VALUES, f"sources.csv line {index} confidence"),
                "notes": (row.get("notes") or "").strip() or None,
            })
        except BatchValidationError as exc:
            errors.extend(exc.errors)

    media: list[dict[str, Any]] = []
    for index, row in enumerate(raw_media, 2):
        try:
            media.append({
                "slug": _required(row.get("college_slug"), f"college_media.csv line {index} slug"),
                "media_type": _required(row.get("media_type"), f"college_media.csv line {index} media_type"),
                "image_url": _url(row.get("image_url"), f"college_media.csv line {index} image_url", required=True),
                "source_url": _url(row.get("source_url"), f"college_media.csv line {index} source_url", required=True),
                "license": _required(row.get("license"), f"college_media.csv line {index} license"),
                "attribution": (row.get("attribution") or "").strip() or None,
                "alt_text": _required(row.get("alt_text"), f"college_media.csv line {index} alt_text"),
                "is_primary": parse_nullable_boolean(row.get("is_primary"), f"college_media.csv line {index} primary") is True,
                "width": _integer(row.get("width"), f"college_media.csv line {index} width"),
                "height": _integer(row.get("height"), f"college_media.csv line {index} height"),
                "verified_at": _iso_datetime(row.get("verified_at"), f"college_media.csv line {index} verified_at"),
            })
        except BatchValidationError as exc:
            errors.extend(exc.errors)

    enrichment: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    enrichment_files: list[tuple[str, Path, int]] = []
    batch_2a_files = list((root / "batch_2a").glob("*Batch2A_50.csv"))
    if batch_2a_files:
        enrichment_files.append(("BATCH_2A", batch_2a_files[0], 3))
    batch_2b_file = root / "batch_2b" / "batch2b_requirements_50.csv"
    if batch_2b_file.is_file():
        enrichment_files.append(("BATCH_2B", batch_2b_file, 0))

    raw_enrichment: list[dict[str, str]] = []
    for batch_name, path, preamble_lines in enrichment_files:
        batch_rows = _read_csv(path, preamble_lines=preamble_lines)
        if len(batch_rows) != EXPECTED_ENRICHMENT_ROWS:
            errors.append(
                f"{batch_name}: expected 50 rows, found {len(batch_rows)}"
            )
        try:
            _validate_unique(batch_rows, "slug", batch_name)
        except BatchValidationError as exc:
            errors.extend(exc.errors)
        for row in batch_rows:
            row["_batch_name"] = batch_name
        raw_enrichment.extend(batch_rows)

    if raw_enrichment:
        try:
            _validate_unique(raw_enrichment, "slug", "combined enrichment")
        except BatchValidationError as exc:
            errors.extend(exc.errors)
        for index, row in enumerate(raw_enrichment, 1):
            batch_name = row["_batch_name"]
            label = f"{batch_name} row {index}"
            try:
                slug = _required(row.get("slug"), f"{label} slug")
                if slug not in slugs:
                    raise BatchValidationError([f"{label}: unknown college slug {slug}"])
                fee = _decimal(row.get("international_application_fee_usd"), f"{label} fee")
                policy = _enum(row.get("test_policy_2026_27"), TEST_POLICIES, f"{label} test policy")
                need_policy = _enum(row.get("international_aid_policy"), NEED_POLICIES, f"{label} aid policy")
                intl_aid, intl_aid_status = _nullable_boolean_with_status(row.get("international_need_based_aid"))
                full_need, full_need_status = _nullable_boolean_with_status(row.get("meets_full_demonstrated_need_international"))
                verified_at = _iso_datetime(row.get("verified_as_of"), f"{label} verified_as_of")
                confidence = _enum(row.get("overall_research_confidence"), CONFIDENCE_VALUES, f"{label} confidence")
                enrichment.append({
                    "batch": batch_name,
                    "slug": slug,
                    "application_platforms": _platforms(
                        row.get("application_platforms"), f"{label} application platforms"
                    ),
                    "test_policy": policy,
                    "test_policy_status": f"{batch_name}_CURRENT",
                    "application_fee_usd": fee,
                    "fee_verification_status": _required(row.get("fee_verification_status"), f"{label} fee status"),
                    "need_policy": need_policy,
                    "aid_policy_status": f"{batch_name}_RESEARCHED",
                    "international_need_based_aid": intl_aid,
                    "international_need_based_aid_status": intl_aid_status,
                    "meets_full_demonstrated_need": full_need,
                    "meets_full_demonstrated_need_status": full_need_status,
                    "aid_forms_or_process": _required(row.get("aid_forms_or_process"), f"{label} aid process"),
                })
                if fee is None:
                    warnings.append(f"unverified fee preserved as NULL: {slug}")
                for column, requirement_type in REQUIREMENT_FIELDS.items():
                    value = (row.get(column) or "").strip()
                    if value:
                        requirements.append({
                            "slug": slug,
                            "requirement_type": requirement_type,
                            "status": _requirement_status(value),
                            "details": value,
                        })
                source_specs = (
                    ("application_source_url", "APPLICATION", "application_requirements"),
                    ("english_source_url", "APPLICATION", "english_requirements"),
                    ("test_policy_source_url", "ADMISSIONS", "test_policy_2026_27"),
                    ("financial_aid_source_url", "FINANCIAL_AID", "international_aid_policy"),
                )
                for column, group, field_name in source_specs:
                    source_url = _url(row.get(column), f"{label} {column}")
                    if source_url:
                        sources.append({
                            "slug": slug,
                            "field_group": group,
                            "field_name": field_name,
                            "source_type": "OFFICIAL_OR_COMMON_APP",
                            "source_url": source_url,
                            "source_cycle": ACADEMIC_CYCLE,
                            "retrieved_at": verified_at,
                            "verified_at": verified_at,
                            "freshness": "CURRENT",
                            "confidence": confidence,
                            "notes": (row.get("research_notes") or "").strip() or None,
                        })
            except BatchValidationError as exc:
                errors.extend(exc.errors)
        conflicts = list((root / "batch_2a").glob("*Conflicts.csv"))
        if conflicts:
            conflict_rows = _read_csv(conflicts[0], preamble_lines=3)
            for row in conflict_rows:
                if (row.get("status") or "").strip().upper() == "OPEN":
                    warnings.append(
                        f"open conflict preserved: {row.get('slug')} / {row.get('field')}"
                    )
    else:
        warnings.append("no Batch 2 enrichment files found; Batch 1 only")

    for group_name, rows in (("sources", sources), ("media", media)):
        unknown = sorted({str(row["slug"]) for row in rows} - slugs)
        if unknown:
            errors.append(f"{group_name}: unknown college slugs: {', '.join(unknown[:5])}")
    if errors:
        raise BatchValidationError(errors)
    return CollegeBatch(colleges, admissions, financial_aid, sources, media, requirements, enrichment, warnings)


def _database_url() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _upsert_source(cursor: Any, college_id: uuid.UUID, row: dict[str, Any]) -> None:
    cursor.execute(
        """
        INSERT INTO college_sources
            (id, college_id, field_group, field_name, source_type, source_url,
             academic_cycle, retrieved_at, verified_at, freshness, confidence, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (college_id, field_group, field_name, source_url, academic_cycle)
        DO UPDATE SET source_type=EXCLUDED.source_type, retrieved_at=EXCLUDED.retrieved_at,
            verified_at=EXCLUDED.verified_at, freshness=EXCLUDED.freshness,
            confidence=EXCLUDED.confidence, notes=EXCLUDED.notes
        """,
        (uuid.uuid4(), college_id, row["field_group"], row["field_name"], row["source_type"],
         row["source_url"], row["source_cycle"], row["retrieved_at"], row["verified_at"],
         row["freshness"], row["confidence"], row["notes"]),
    )


def import_batch(
    batch: CollegeBatch,
    *,
    environment: str | None = None,
    dry_run: bool = False,
    database_url: str | None = None,
) -> ImportReport:
    report = ImportReport(
        files_read=7 if batch.enrichment else 5,
        rows_read=sum(len(rows) for rows in (batch.colleges, batch.admissions, batch.financial_aid, batch.sources, batch.media, batch.requirements, batch.enrichment)),
        valid_rows=sum(len(rows) for rows in (batch.colleges, batch.admissions, batch.financial_aid, batch.sources, batch.media, batch.requirements, batch.enrichment)),
        warnings=len(batch.warnings),
        colleges_upserted=len(batch.colleges),
        admissions_upserted=len(batch.admissions) + len(batch.enrichment),
        financial_aid_upserted=len(batch.financial_aid) + len(batch.enrichment),
        requirements_upserted=len(batch.requirements),
        sources_upserted=len(batch.sources),
        media_upserted=len(batch.media),
        dry_run=dry_run,
    )
    if dry_run:
        return report
    normalized_environment = (environment or "").strip().lower()
    if not normalized_environment:
        raise ValueError("database writes require explicit --environment local or staging")
    if normalized_environment not in {"local", "staging"}:
        raise ValueError("only local or staging imports are allowed")
    if os.getenv("APP_ENV", "").strip().lower() == "production":
        raise ValueError("refusing college batch import while APP_ENV=production")

    with connect_database(database_url or _database_url()) as connection, connection.cursor() as cursor:
        college_ids: dict[str, uuid.UUID] = {}
        for row in batch.colleges:
            cursor.execute(
                """
                INSERT INTO colleges
                    (id, slug, name, official_name, normalized_name, ipeds_id, country_code,
                     state_region, city, institution_type, selection_group,
                     application_platform_primary, application_platforms, official_website,
                     common_app_member, identity_confidence, active, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())
                ON CONFLICT (slug) DO UPDATE SET name=EXCLUDED.name,
                    official_name=EXCLUDED.official_name, normalized_name=EXCLUDED.normalized_name,
                    ipeds_id=EXCLUDED.ipeds_id, country_code=EXCLUDED.country_code,
                    state_region=EXCLUDED.state_region, city=EXCLUDED.city,
                    institution_type=EXCLUDED.institution_type,
                    selection_group=EXCLUDED.selection_group,
                    application_platform_primary=EXCLUDED.application_platform_primary,
                    application_platforms=EXCLUDED.application_platforms,
                    official_website=EXCLUDED.official_website,
                    common_app_member=EXCLUDED.common_app_member,
                    identity_confidence=EXCLUDED.identity_confidence,
                    active=EXCLUDED.active, updated_at=now()
                RETURNING id
                """,
                (uuid.uuid4(), row["slug"], row["name"], row["official_name"],
                 row["normalized_name"], row["ipeds_id"], row["country_code"],
                 row["state_region"], row["city"], row["institution_type"],
                 row["selection_group"], row["application_platform_primary"],
                 Jsonb(row["application_platforms"]), row["official_website"],
                 row["common_app_member"], row["identity_confidence"], row["active"]),
            )
            college_ids[row["slug"]] = cursor.fetchone()[0]
        for row in batch.admissions:
            cursor.execute(
                """
                INSERT INTO college_admissions
                    (id,college_id,academic_cycle,source_cycle,applicants_total,admits_total,
                     enrolled_total,acceptance_rate,yield_rate_pct,sat_25,sat_50,sat_75,act_25,act_50,act_75,
                     test_policy,test_policy_status,application_fee_usd)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (college_id,academic_cycle) DO UPDATE SET
                    source_cycle=EXCLUDED.source_cycle, applicants_total=EXCLUDED.applicants_total,
                    admits_total=EXCLUDED.admits_total, enrolled_total=EXCLUDED.enrolled_total,
                    acceptance_rate=EXCLUDED.acceptance_rate,
                    yield_rate_pct=EXCLUDED.yield_rate_pct, sat_25=EXCLUDED.sat_25,
                    sat_50=EXCLUDED.sat_50, sat_75=EXCLUDED.sat_75, act_25=EXCLUDED.act_25,
                    act_50=EXCLUDED.act_50, act_75=EXCLUDED.act_75,
                    test_policy=EXCLUDED.test_policy, test_policy_status=EXCLUDED.test_policy_status,
                    application_fee_usd=EXCLUDED.application_fee_usd, updated_at=now()
                """,
                (uuid.uuid4(), college_ids[row["slug"]], ACADEMIC_CYCLE, row["source_cycle"],
                 row["applicants_total"], row["admits_total"], row["enrolled_total"],
                 row["acceptance_rate"], row["yield_rate_pct"], row["sat_25"], row["sat_50"], row["sat_75"],
                 row["act_25"], row["act_50"], row["act_75"], row["test_policy"],
                 row["test_policy_status"], row["application_fee_usd"]),
            )
        for row in batch.financial_aid:
            cursor.execute(
                """
                INSERT INTO college_financial_aid
                    (id,college_id,academic_cycle,source_cycle,need_policy,aid_policy_status,
                     international_need_based_aid,international_need_based_aid_status,
                     meets_full_demonstrated_need,meets_full_demonstrated_need_status,
                     tuition,mandatory_fees,room_board,estimated_cost_of_attendance,cost_basis,
                     currency,notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (college_id,academic_cycle) DO UPDATE SET
                    source_cycle=EXCLUDED.source_cycle, need_policy=EXCLUDED.need_policy,
                    aid_policy_status=EXCLUDED.aid_policy_status,
                    international_need_based_aid=EXCLUDED.international_need_based_aid,
                    international_need_based_aid_status=EXCLUDED.international_need_based_aid_status,
                    meets_full_demonstrated_need=EXCLUDED.meets_full_demonstrated_need,
                    meets_full_demonstrated_need_status=EXCLUDED.meets_full_demonstrated_need_status,
                    tuition=EXCLUDED.tuition, mandatory_fees=EXCLUDED.mandatory_fees,
                    room_board=EXCLUDED.room_board,
                    estimated_cost_of_attendance=EXCLUDED.estimated_cost_of_attendance,
                    cost_basis=EXCLUDED.cost_basis, currency=EXCLUDED.currency,
                    notes=EXCLUDED.notes, updated_at=now()
                """,
                (uuid.uuid4(), college_ids[row["slug"]], ACADEMIC_CYCLE, row["source_cycle"],
                 row["need_policy"], row["aid_policy_status"], row["international_need_based_aid"],
                 row["international_need_based_aid_status"], row["meets_full_demonstrated_need"],
                 row["meets_full_demonstrated_need_status"], row["tuition"], row["mandatory_fees"],
                 row["room_board"], row["estimated_cost_of_attendance"], row["cost_basis"],
                 row["currency"], row["notes"]),
            )
        for row in batch.enrichment:
            cursor.execute(
                """
                UPDATE college_admissions SET test_policy=%s, test_policy_status=%s,
                    application_fee_usd=COALESCE(%s,application_fee_usd),
                    application_fee_status=%s, updated_at=now()
                WHERE college_id=%s AND academic_cycle=%s
                """,
                (row["test_policy"], row["test_policy_status"], row["application_fee_usd"],
                 row["fee_verification_status"],
                 college_ids[row["slug"]], ACADEMIC_CYCLE),
            )
            cursor.execute(
                "UPDATE colleges SET application_platforms=%s, updated_at=now() WHERE id=%s",
                (Jsonb(row["application_platforms"]), college_ids[row["slug"]]),
            )
            cursor.execute(
                """
                UPDATE college_financial_aid SET need_policy=%s, aid_policy_status=%s,
                    international_need_based_aid=%s, international_need_based_aid_status=%s,
                    meets_full_demonstrated_need=%s, meets_full_demonstrated_need_status=%s,
                    aid_forms_or_process=%s, updated_at=now()
                WHERE college_id=%s AND academic_cycle=%s
                """,
                (row["need_policy"], row["aid_policy_status"], row["international_need_based_aid"],
                 row["international_need_based_aid_status"], row["meets_full_demonstrated_need"],
                 row["meets_full_demonstrated_need_status"], row["aid_forms_or_process"],
                 college_ids[row["slug"]], ACADEMIC_CYCLE),
            )
        for row in batch.requirements:
            cursor.execute(
                """
                INSERT INTO college_requirements
                    (id,college_id,academic_cycle,requirement_type,status,details)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (college_id,academic_cycle,requirement_type) DO UPDATE SET
                    status=EXCLUDED.status, details=EXCLUDED.details
                """,
                (uuid.uuid4(), college_ids[row["slug"]], ACADEMIC_CYCLE,
                 row["requirement_type"], row["status"], row["details"]),
            )
        for row in batch.sources:
            _upsert_source(cursor, college_ids[row["slug"]], row)
        for row in batch.media:
            cursor.execute(
                """
                INSERT INTO college_media
                    (id,college_id,media_type,image_url,source_url,license,attribution,
                     alt_text,is_primary,width,height,verified_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (college_id,image_url) DO UPDATE SET media_type=EXCLUDED.media_type,
                    source_url=EXCLUDED.source_url, license=EXCLUDED.license,
                    attribution=EXCLUDED.attribution, alt_text=EXCLUDED.alt_text,
                    is_primary=EXCLUDED.is_primary, width=EXCLUDED.width,
                    height=EXCLUDED.height, verified_at=EXCLUDED.verified_at
                """,
                (uuid.uuid4(), college_ids[row["slug"]], row["media_type"], row["image_url"],
                 row["source_url"], row["license"], row["attribution"], row["alt_text"],
                 row["is_primary"], row["width"], row["height"], row["verified_at"]),
            )
    return report


def _print_report(report: ImportReport, warnings: list[str]) -> None:
    for name in (
        "files_read", "rows_read", "valid_rows", "rejected_rows", "warnings",
        "colleges_upserted", "admissions_upserted", "financial_aid_upserted",
        "requirements_upserted", "sources_upserted", "media_upserted",
    ):
        print(f"{name.replace('_', ' ')}: {getattr(report, name)}")
    for warning in warnings:
        print(f"  - {warning}")
    if report.dry_run:
        print("dry run: no database connection opened; no rows written")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--environment", choices=("local", "staging"))
    args = parser.parse_args()
    batch = parse_batch(args.directory)
    report = import_batch(batch, environment=args.environment, dry_run=args.dry_run)
    _print_report(report, batch.warnings)


if __name__ == "__main__":
    main()
