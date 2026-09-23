"""Validate, download, and optionally import curated Evalio college logos."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import socket
import struct
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

from scripts.import_college_media import import_media, parse_csv

ALLOWED_HOSTS = {"commons.wikimedia.org", "upload.wikimedia.org", "thumb.wikimedia.org"}
ALLOWED_CONTENT_TYPES = {"image/svg+xml", "image/png", "image/jpeg", "image/webp"}
ALLOWED_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
CONTENT_TYPE_BY_EXTENSION = {
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".webp": "image/webp",
}
MAX_BYTES = 5 * 1024 * 1024
EXPECTED_ROWS = 25
SYSTEM_GETADDRINFO = socket.getaddrinfo


def _ipv4_getaddrinfo(
    host: str | bytes | None,
    port: str | int | None,
    family: int = 0,
    type: int = 0,
    proto: int = 0,
    flags: int = 0,
) -> list[tuple[int, int, int, str, tuple[str, int]]]:
    """Resolve only IPv4 for Wikimedia, whose IPv6 edge may apply a separate throttle."""
    return SYSTEM_GETADDRINFO(  # type: ignore[return-value]
        host, port, socket.AF_INET, type, proto, flags
    )


@dataclass(frozen=True)
class LogoManifestRow:
    college_slug: str
    school_name: str
    download_url: str | None
    source_url: str | None
    source_provenance: str
    license_or_status: str
    trademark_notice: str
    verification_quality: str
    repo_path: Path | None
    public_url: str | None
    alt_text: str
    verified_at: str


def _clean(value: str | None) -> str:
    return " ".join((value or "").split())


def read_manifest(path: Path) -> list[LogoManifestRow]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if len(raw_rows) != EXPECTED_ROWS:
        raise ValueError(f"manifest must contain exactly {EXPECTED_ROWS} rows")
    rows: list[LogoManifestRow] = []
    seen_slugs: set[str] = set()
    seen_orders: set[int] = set()
    for line, raw in enumerate(raw_rows, 2):
        try:
            order = int(raw["seed_order"])
            slug = raw["college_slug"].strip()
            download_url = raw["asset_download_url"].strip() or None
            source_url = raw["source_page_url"].strip() or None
            repo_value = raw["recommended_repo_path"].strip()
            public_url = raw["public_url_after_import"].strip() or None
            quality = raw["verification_quality"].strip().upper()
            status = raw["license_or_status"].strip()
            if order in seen_orders or slug in seen_slugs:
                raise ValueError("duplicate seed_order or college_slug")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
                raise ValueError("invalid college_slug")
            if raw["media_type"].strip().upper() != "LOGO":
                raise ValueError("media_type must be LOGO")
            if quality not in {"HIGH", "MEDIUM", "PENDING_OFFICIAL_DOWNLOAD"}:
                raise ValueError("invalid verification_quality")
            if raw["trademark_notice"].strip().upper() not in {"YES", "NO"}:
                raise ValueError("trademark_notice must be YES or NO")
            if not _clean(raw["school_name"]) or not _clean(raw["alt_text"]) or not status:
                raise ValueError("school_name, alt_text, and license_or_status are required")
            if bool(download_url) != bool(repo_value) or bool(download_url) != bool(public_url):
                raise ValueError("download URL, repository path, and public URL must be all set or blank")
            repo_path: Path | None = None
            if download_url:
                parsed = urlparse(download_url)
                source = urlparse(source_url or "")
                if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
                    raise ValueError("download URL host is not approved")
                if source.scheme != "https" or source.hostname not in ALLOWED_HOSTS:
                    raise ValueError("source URL host is not approved")
                repo_path = Path(repo_value)
                expected_prefix = Path("public") / "college-logos"
                if repo_path.parent != expected_prefix or repo_path.stem != slug:
                    raise ValueError("repository path must use public/college-logos/{college_slug}")
                if repo_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                    raise ValueError("unsupported asset extension")
                if public_url != f"/college-logos/{repo_path.name}":
                    raise ValueError("public URL does not match repository path")
            elif quality != "PENDING_OFFICIAL_DOWNLOAD":
                raise ValueError("only pending official assets may omit download details")
            datetime.fromisoformat(raw["verified_at"])
            seen_orders.add(order)
            seen_slugs.add(slug)
            rows.append(
                LogoManifestRow(
                    slug, _clean(raw["school_name"]), download_url, source_url,
                    _clean(raw["source_provenance"]), status,
                    raw["trademark_notice"].strip().upper(), quality, repo_path,
                    public_url, _clean(raw["alt_text"]), raw["verified_at"].strip(),
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"line {line}: {error}") from error
    return rows


def _svg_dimensions(root: ET.Element) -> tuple[int | None, int | None]:
    def number(value: str | None) -> int | None:
        match = re.match(r"^([0-9]+(?:\.[0-9]+)?)", value or "")
        return round(float(match.group(1))) if match else None

    width, height = number(root.get("width")), number(root.get("height"))
    if width and height:
        return width, height
    view_box = (root.get("viewBox") or "").split()
    if len(view_box) == 4:
        return round(float(view_box[2])), round(float(view_box[3]))
    return None, None


def validate_asset(data: bytes, extension: str, declared_type: str) -> tuple[str, int | None, int | None]:
    if not data or len(data) > MAX_BYTES:
        raise ValueError("asset is empty or exceeds 5 MB")
    prefix = data[:512].lstrip().lower()
    if prefix.startswith((b"<!doctype html", b"<html")) or b"<title>login" in prefix:
        raise ValueError("received HTML/login content instead of an image")
    extension = extension.lower()
    detected: str
    width: int | None = None
    height: int | None = None
    if extension == ".svg":
        try:
            root = ET.fromstring(data)
        except ET.ParseError as error:
            raise ValueError("invalid SVG XML") from error
        if root.tag.rsplit("}", 1)[-1].lower() != "svg":
            raise ValueError("SVG payload has no svg root")
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1].lower() == "script":
                raise ValueError("SVG scripts are not allowed")
            if any(name.lower().startswith("on") for name in element.attrib):
                raise ValueError("SVG event handlers are not allowed")
            for name, value in element.attrib.items():
                if name.rsplit("}", 1)[-1].lower() == "href" and value.lstrip().lower().startswith(
                    ("http:", "https:", "//")
                ):
                    raise ValueError("external SVG resources are not allowed")
        detected = "image/svg+xml"
        width, height = _svg_dimensions(root)
    elif extension == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "image/png"
        width, height = struct.unpack(">II", data[16:24])
    elif extension in {".jpg", ".jpeg"} and data.startswith(b"\xff\xd8\xff"):
        detected = "image/jpeg"
    elif extension == ".webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        detected = "image/webp"
    else:
        raise ValueError("file signature does not match its extension")
    if declared_type not in ALLOWED_CONTENT_TYPES or declared_type != detected:
        raise ValueError(f"content type mismatch: declared {declared_type}, detected {detected}")
    return detected, width, height


def download_asset(
    row: LogoManifestRow, repo_root: Path
) -> tuple[int, str, str, int | None, int | None, Path]:
    if not row.download_url or not row.repo_path:
        raise ValueError("row has no approved download")
    destination = (repo_root / row.repo_path).resolve()
    approved_root = (repo_root / "public" / "college-logos").resolve()
    if destination.parent != approved_root:
        raise ValueError("destination escaped public/college-logos")
    if destination.exists():
        data = destination.read_bytes()
        expected_type = CONTENT_TYPE_BY_EXTENSION[row.repo_path.suffix.lower()]
        detected, width, height = validate_asset(data, row.repo_path.suffix, expected_type)
        return len(data), detected, hashlib.sha256(data).hexdigest(), width, height, destination
    thumbnail_destination = destination.with_suffix(".png")
    if row.repo_path.suffix.lower() == ".svg" and thumbnail_destination.exists():
        data = thumbnail_destination.read_bytes()
        detected, width, height = validate_asset(data, ".png", "image/png")
        return (
            len(data), detected, hashlib.sha256(data).hexdigest(), width, height,
            thumbnail_destination,
        )
    filename = unquote(urlparse(row.download_url).path.rsplit("/", 1)[-1])
    digest = hashlib.md5(filename.encode(), usedforsecurity=False).hexdigest()
    direct_url = (
        f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/"
        f"{quote(filename)}"
    )
    urls = [row.download_url, direct_url]
    original_getaddrinfo = socket.getaddrinfo
    try:
        socket.getaddrinfo = _ipv4_getaddrinfo  # type: ignore[assignment]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for attempt in range(2):
            try:
                request = urllib.request.Request(
                    urls[min(attempt, 1)],
                    headers={"User-Agent": "EvalioCollegeLogoImporter/2.0 (+local curated asset import)"},
                )
                with opener.open(request, timeout=45) as response:
                    content_type = response.headers.get_content_type()
                    data = response.read(MAX_BYTES + 1)
                break
            except urllib.error.HTTPError as error:
                if error.code == 429:
                    if row.repo_path.suffix.lower() != ".svg":
                        retry_after = error.headers.get("Retry-After", "later")
                        raise ValueError(
                            f"upstream rate limit; retry after {retry_after} seconds"
                        ) from error
                    thumbnail_url = (
                        "https://thumb.wikimedia.org/wikipedia/commons/thumb/"
                        f"{digest[0]}/{digest[:2]}/{quote(filename)}/"
                        f"500px-{quote(filename)}.png"
                    )
                    thumbnail_request = urllib.request.Request(
                        thumbnail_url,
                        headers={
                            "User-Agent": "EvalioCollegeLogoImporter/2.0 "
                            "(+local curated asset import)"
                        },
                    )
                    with opener.open(thumbnail_request, timeout=45) as response:
                        content_type = response.headers.get_content_type()
                        data = response.read(MAX_BYTES + 1)
                    destination = thumbnail_destination
                    break
                if attempt == 1:
                    raise
    finally:
        socket.getaddrinfo = original_getaddrinfo
    detected, width, height = validate_asset(data, destination.suffix, content_type)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(destination)
    return len(data), detected, hashlib.sha256(data).hexdigest(), width, height, destination


def write_media_csv(path: Path, records: list[dict[str, str]]) -> None:
    fields = [
        "college_slug", "media_type", "image_url", "source_url", "license",
        "attribution", "alt_text", "is_primary", "width", "height", "verified_at",
        "sha256", "content_type", "verification_quality", "trademark_notice",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--download", action="store_true", help="download approved assets locally")
    parser.add_argument("--write-media-csv", action="store_true")
    parser.add_argument("--import-database", action="store_true")
    parser.add_argument("--confirm", choices=("IMPORT",))
    args = parser.parse_args()
    if args.import_database and (not args.download or args.confirm != "IMPORT"):
        parser.error("database import requires --download --import-database --confirm IMPORT")

    rows = read_manifest(args.manifest)
    repo_root = Path(__file__).resolve().parents[1]
    records: list[dict[str, str]] = []
    failures: list[tuple[str, str]] = []
    for row in rows:
        if not row.download_url:
            print(f"SKIP {row.college_slug}: approved official asset is pending")
            continue
        try:
            if args.download:
                size, content_type, sha256, width, height, destination = download_asset(
                    row, repo_root
                )
                public_url = f"/college-logos/{destination.name}"
                print(
                    f"OK   {row.college_slug} -> "
                    f"{destination.relative_to(repo_root)} ({size} bytes)"
                )
            else:
                content_type = sha256 = ""
                width = height = None
                public_url = row.public_url or ""
            verified = datetime.fromisoformat(row.verified_at)
            if verified.tzinfo is None:
                verified = verified.replace(tzinfo=UTC)
            records.append(
                {
                    "college_slug": row.college_slug, "media_type": "LOGO",
                    "image_url": public_url, "source_url": row.source_url or "",
                    "license": row.license_or_status, "attribution": row.source_provenance,
                    "alt_text": row.alt_text, "is_primary": "YES",
                    "width": str(width or ""), "height": str(height or ""),
                    "verified_at": verified.isoformat(), "sha256": sha256,
                    "content_type": content_type,
                    "verification_quality": row.verification_quality,
                    "trademark_notice": row.trademark_notice,
                }
            )
        except Exception as error:  # noqa: BLE001 - report every asset without partial DB writes
            failures.append((row.college_slug, str(error)))
            print(f"FAIL {row.college_slug}: {error}", file=sys.stderr)

    output = args.manifest.parent / "college_media_logo_import.csv"
    if args.write_media_csv:
        write_media_csv(output, records)
        suffix = " (validated rows only)" if failures else ""
        print(f"Wrote {output}{suffix}")
    if failures:
        print(
            "Some assets failed validation; they remain on fallback and no database import was performed.",
            file=sys.stderr,
        )
        return 2
    if args.import_database:
        imported = parse_csv(output)
        inserted, updated = import_media(imported, dry_run=False)
        print(f"media inserted/updated: {inserted}/{updated}")
    print(f"manifest rows: {len(rows)}; ready logos: {len(records)}; pending: {len(rows) - len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
