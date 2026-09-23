#!/usr/bin/env python3
"""
Download curated Evalio college logos from their original upstream sources.

This script DOES NOT generate or redraw logos.
It downloads only entries listed in college_logos_batch2.csv.

Run from repository root:
    python scripts/import_college_logos_batch2.py data/research/logo-batch2/college_logos_batch2.csv --download
    python scripts/import_college_logos_batch2.py data/research/logo-batch2/college_logos_batch2.csv --download --write-media-csv
"""
from __future__ import annotations
import argparse, csv, hashlib, sys, urllib.request
from pathlib import Path

ALLOWED_CONTENT_TYPES = {"image/svg+xml","image/png","image/jpeg","image/webp"}
MAX_BYTES = 5 * 1024 * 1024

def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "EvalioLogoImporter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        content_type = response.headers.get_content_type()
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("asset exceeds 5 MB")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"unexpected content type: {content_type}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return len(data), content_type, hashlib.sha256(data).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--write-media-csv", action="store_true")
    args = ap.parse_args()

    rows = read_rows(args.manifest)
    repo_root = Path.cwd()
    out_rows, failures = [], []

    for row in rows:
        url = (row.get("asset_download_url") or "").strip()
        repo_path = (row.get("recommended_repo_path") or "").strip()
        if not url or not repo_path:
            print(f"SKIP {row['college_slug']}: approved downloadable asset not available")
            continue
        dest = repo_root / repo_path
        try:
            if args.download:
                size, content_type, sha = download(url, dest)
                print(f"OK   {row['college_slug']} -> {repo_path} ({size} bytes)")
            else:
                size, content_type, sha = "", "", ""
            out_rows.append({
                "college_slug": row["college_slug"],
                "media_type": "LOGO",
                "image_url": row["public_url_after_import"],
                "source_url": row["source_page_url"],
                "license": row["license_or_status"],
                "attribution": row["source_provenance"],
                "alt_text": row["alt_text"],
                "is_primary": "true",
                "verified_at": row["verified_at"],
                "sha256": sha,
                "content_type": content_type,
            })
        except Exception as exc:
            failures.append((row["college_slug"], str(exc)))
            print(f"FAIL {row['college_slug']}: {exc}", file=sys.stderr)

    if args.write_media_csv:
        out = args.manifest.parent / "college_media_logo_import_batch2.csv"
        fields = ["college_slug","media_type","image_url","source_url","license","attribution","alt_text","is_primary","verified_at","sha256","content_type"]
        with out.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(out_rows)
        print(f"Wrote {out}")

    if failures:
        print("\nSome assets failed. Do not replace them with guessed/athletics logos.", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
