"""Validate and import curated, licensed college media records."""

from __future__ import annotations

import argparse
import csv
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import psycopg

from api.admission_engine.config import get_settings

ALLOWED_LICENSES = {"PUBLIC_DOMAIN", "CC0", "CC_BY_2_0", "CC_BY_2_5", "CC_BY_3_0", "CC_BY_4_0", "CC_BY_SA_2_0", "CC_BY_SA_3_0", "CC_BY_SA_4_0"}
ALLOWED_MEDIA_TYPES = {"CAMPUS", "BUILDING", "GALLERY", "LOGO"}
ALLOWED_IMAGE_HOSTS = {"commons.wikimedia.org", "upload.wikimedia.org"}
connect_database = psycopg.connect


@dataclass(frozen=True)
class MediaRow:
    college_slug: str
    media_type: str
    image_url: str
    source_url: str
    license: str
    attribution: str | None
    alt_text: str
    is_primary: bool
    width: int | None
    height: int | None
    sha256: str | None
    content_type: str | None
    verification_quality: str | None
    trademark_notice: bool | None
    verified_at: datetime


def _url(value: str, *, image: bool = False) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("media URLs must be credential-free HTTPS URLs")
    if image and parsed.hostname not in ALLOWED_IMAGE_HOSTS:
        raise ValueError(f"image host is not allowlisted: {parsed.hostname}")
    return value.strip()


def _optional_dimension(value: str) -> int | None:
    if not value.strip():
        return None
    result = int(value)
    if result <= 0 or result > 30_000:
        raise ValueError("media dimensions must be between 1 and 30000")
    return result


def _image_url(value: str, media_type: str) -> str:
    value = value.strip()
    if media_type == "LOGO":
        if not re.fullmatch(r"/college-logos/[a-z0-9-]+\.(?:svg|png|jpe?g|webp)", value):
            raise ValueError("logo image_url must be a safe /college-logos/ path")
        return value
    return _url(value, image=True)


def _optional_bool(value: str) -> bool | None:
    normalized = value.strip().upper()
    if not normalized:
        return None
    if normalized not in {"YES", "NO"}:
        raise ValueError("trademark_notice must be YES, NO, or blank")
    return normalized == "YES"


def parse_csv(path: Path) -> list[MediaRow]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if not raw_rows:
        raise ValueError("media CSV is empty")
    rows: list[MediaRow] = []
    seen: set[tuple[str, str]] = set()
    primary_slugs: set[str] = set()
    for line, raw in enumerate(raw_rows, 2):
        try:
            slug = raw["college_slug"].strip()
            media_type = raw["media_type"].strip().upper()
            license_name = raw["license"].strip()
            alt_text = " ".join(raw["alt_text"].split())
            primary_value = raw["is_primary"].strip().upper()
            if primary_value not in {"YES", "NO"}:
                raise ValueError("is_primary must be YES or NO")
            is_primary = primary_value == "YES"
            if not slug or not alt_text:
                raise ValueError("college_slug and alt_text are required")
            if media_type not in ALLOWED_MEDIA_TYPES:
                raise ValueError("media type is not allowed")
            if not license_name or (media_type != "LOGO" and license_name.upper() not in ALLOWED_LICENSES):
                raise ValueError("license is not allowed")
            key = (slug, raw["image_url"].strip())
            if key in seen:
                raise ValueError("duplicate college/image pair")
            if is_primary and slug in primary_slugs:
                raise ValueError("a college may have only one primary image")
            seen.add(key)
            if is_primary:
                primary_slugs.add(slug)
            verified_at = datetime.fromisoformat(raw["verified_at"])
            if verified_at.tzinfo is None:
                raise ValueError("verified_at must include a timezone")
            sha256 = (raw.get("sha256") or "").strip().lower() or None
            if sha256 and not re.fullmatch(r"[0-9a-f]{64}", sha256):
                raise ValueError("sha256 must contain 64 lowercase hexadecimal characters")
            content_type = (raw.get("content_type") or "").strip() or None
            verification_quality = (raw.get("verification_quality") or "").strip().upper() or None
            if verification_quality and verification_quality not in {"HIGH", "MEDIUM", "LOW"}:
                raise ValueError("verification_quality is not allowed")
            rows.append(
                MediaRow(
                    slug,
                    media_type,
                    _image_url(raw["image_url"], media_type),
                    _url(raw["source_url"]),
                    license_name,
                    raw["attribution"].strip() or None,
                    alt_text,
                    is_primary,
                    _optional_dimension(raw["width"]),
                    _optional_dimension(raw["height"]),
                    sha256,
                    content_type,
                    verification_quality,
                    _optional_bool(raw.get("trademark_notice") or ""),
                    verified_at,
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"line {line}: {error}") from error
    return rows


def import_media(rows: list[MediaRow], *, dry_run: bool, database_url: str | None = None) -> tuple[int, int]:
    if dry_run:
        return len(rows), 0
    configured = get_settings().DATABASE_URL
    url = database_url or (configured.get_secret_value() if configured else None)
    if not url:
        raise ValueError("DATABASE_URL is required")
    url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    inserted = updated = 0
    with connect_database(url) as connection, connection.cursor() as cursor:
        slugs = [row.college_slug for row in rows]
        cursor.execute("SELECT slug, id FROM colleges WHERE slug = ANY(%s)", (slugs,))
        college_ids = dict(cursor.fetchall())
        missing = sorted(set(slugs) - college_ids.keys())
        if missing:
            raise ValueError(f"college slugs not found: {', '.join(missing)}")
        for row in rows:
            cursor.execute("SELECT id FROM college_media WHERE college_id = %s AND image_url = %s", (college_ids[row.college_slug], row.image_url))
            exists = cursor.fetchone() is not None
            if row.is_primary:
                cursor.execute(
                    "UPDATE college_media SET is_primary = FALSE WHERE college_id = %s AND media_type = %s",
                    (college_ids[row.college_slug], row.media_type),
                )
            cursor.execute(
                """INSERT INTO college_media (id, college_id, media_type, image_url, source_url, license, attribution, alt_text, is_primary, width, height, sha256, content_type, verification_quality, trademark_notice, verified_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (college_id, image_url) DO UPDATE SET media_type = EXCLUDED.media_type, source_url = EXCLUDED.source_url, license = EXCLUDED.license, attribution = EXCLUDED.attribution, alt_text = EXCLUDED.alt_text, is_primary = EXCLUDED.is_primary, width = EXCLUDED.width, height = EXCLUDED.height, sha256 = EXCLUDED.sha256, content_type = EXCLUDED.content_type, verification_quality = EXCLUDED.verification_quality, trademark_notice = EXCLUDED.trademark_notice, verified_at = EXCLUDED.verified_at""",
                (
                    uuid.uuid4(), college_ids[row.college_slug], row.media_type,
                    row.image_url, row.source_url, row.license, row.attribution,
                    row.alt_text, row.is_primary, row.width, row.height, row.sha256,
                    row.content_type, row.verification_quality, row.trademark_notice,
                    row.verified_at,
                ),
            )
            updated += int(exists)
            inserted += int(not exists)
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm", choices=("IMPORT",))
    args = parser.parse_args()
    rows = parse_csv(args.file)
    if not args.dry_run and args.confirm != "IMPORT":
        parser.error("database writes require --confirm IMPORT")
    inserted, updated = import_media(rows, dry_run=args.dry_run)
    print(f"rows read: {len(rows)}")
    print(f"valid rows: {len(rows)}")
    print(f"media inserted/updated: {inserted}/{updated}")
    print(f"dry run: {'yes' if args.dry_run else 'no'}")


if __name__ == "__main__":
    main()
