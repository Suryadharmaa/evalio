from pathlib import Path

import pytest

from scripts.import_college_logos import read_manifest, validate_asset
from scripts.import_college_media import parse_csv

MANIFEST = Path("data/research/logo-batch1/college_logos_batch1.csv")
MANIFEST_BATCH_2 = Path("data/research/logo-batch2/college_logos_batch2.csv")
MANIFEST_BATCH_3 = Path("data/research/logo-batch3/college_logos_batch3.csv")
MANIFEST_BATCH_4 = Path("data/research/logo-batch4/college_logos_batch4.csv")


def test_batch_one_manifest_is_complete_and_has_one_intentional_fallback() -> None:
    rows = read_manifest(MANIFEST)

    assert len(rows) == 25
    assert len({row.college_slug for row in rows}) == 25
    assert sum(row.download_url is not None for row in rows) == 24
    pending = [row for row in rows if row.download_url is None]
    assert [row.college_slug for row in pending] == ["university-of-notre-dame"]
    assert pending[0].verification_quality == "PENDING_OFFICIAL_DOWNLOAD"


@pytest.mark.parametrize(
    ("manifest", "ready", "pending"),
    [
        (MANIFEST_BATCH_2, 13, 12),
        (MANIFEST_BATCH_3, 15, 10),
        (MANIFEST_BATCH_4, 18, 7),
    ],
)
def test_later_manifests_are_complete(
    manifest: Path, ready: int, pending: int
) -> None:
    rows = read_manifest(manifest)

    assert len(rows) == 25
    assert len({row.college_slug for row in rows}) == 25
    assert sum(row.download_url is not None for row in rows) == ready
    assert sum(row.download_url is None for row in rows) == pending


def test_identity_sensitive_logo_rows_match_corrected_institutions() -> None:
    rows = {
        row.college_slug: row.school_name
        for manifest in (MANIFEST_BATCH_2, MANIFEST_BATCH_3, MANIFEST_BATCH_4)
        for row in read_manifest(manifest)
    }

    assert rows["purdue-university"] == "Purdue University"
    assert rows["texas-a-and-m-university"] == "Texas A&M University"
    assert rows["north-carolina-state-university"] == "North Carolina State University at Raleigh"
    assert rows["arizona-state-university"] == "Arizona State University Campus Immersion"


def test_asset_validator_rejects_html_disguised_as_svg() -> None:
    with pytest.raises(ValueError, match="HTML/login"):
        validate_asset(b"<!doctype html><title>Login</title>", ".svg", "image/svg+xml")


def test_asset_validator_accepts_safe_svg_and_reports_dimensions() -> None:
    data = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 64"><path d="M0 0"/></svg>'

    assert validate_asset(data, ".svg", "image/svg+xml") == ("image/svg+xml", 180, 64)


def test_media_parser_accepts_local_verified_logo(tmp_path: Path) -> None:
    csv_path = tmp_path / "logos.csv"
    csv_path.write_text(
        "college_slug,media_type,image_url,source_url,license,attribution,alt_text,is_primary,width,height,verified_at,sha256,content_type,verification_quality,trademark_notice\n"
        "example-university,LOGO,/college-logos/example-university.svg,https://commons.wikimedia.org/wiki/File:Example.svg,PD-textlogo,Wikimedia Commons,Example University logo,YES,180,64,2026-09-20T00:00:00+00:00,"
        + "a" * 64
        + ",image/svg+xml,HIGH,YES\n",
        encoding="utf-8",
    )

    row = parse_csv(csv_path)[0]
    assert row.media_type == "LOGO"
    assert row.image_url == "/college-logos/example-university.svg"
    assert row.verification_quality == "HIGH"
    assert row.trademark_notice is True


def test_media_parser_rejects_logo_path_outside_approved_directory(tmp_path: Path) -> None:
    csv_path = tmp_path / "logos.csv"
    csv_path.write_text(
        "college_slug,media_type,image_url,source_url,license,attribution,alt_text,is_primary,width,height,verified_at\n"
        "example-university,LOGO,/uploads/example.svg,https://commons.wikimedia.org/wiki/File:Example.svg,PD-textlogo,,Example logo,YES,,,2026-09-20T00:00:00+00:00\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="safe /college-logos/"):
        parse_csv(csv_path)
