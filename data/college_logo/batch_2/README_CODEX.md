# Evalio College Logos — Batch 2 (#26–50)

Purpose: curated, source-backed logo manifest for colleges 26–50 in Evalio's 100-school seed.

This package does **not** generate or redraw logos. It tells Codex where verified or official-source logo assets should come from and how to place them into the repo.

## Coverage snapshot

- 25 colleges reviewed
- 11 entries have a ready download URL in this manifest
- 14 entries are intentionally `PENDING_OFFICIAL_DOWNLOAD` because the safest source is the official university brand portal rather than an unverified derivative or athletics mark

This batch is more mixed than Batch 1 because several schools either:
- restrict direct brand downloads,
- have multiple sub-brand / athletics logo variants,
- or need a safer institutional-logo check before local import.

## Important identity corrections

Two colleges in the underlying seed required identity correction. Codex must preserve the slug but resolve to the corrected institution identity:

```text
purdue-university            -> Purdue University (Main Campus / West Lafayette), NOT Purdue University Global
texas-a-and-m-university     -> Texas A&M University (College Station), NOT West Texas A & M University
```

Do not import a logo for the incorrect institution.

## Required repository folders

Create only if missing:

```text
public/
└── college-logos/

data/
└── research/
    └── logo-batch2/
        ├── college_logos_batch2.csv
        └── README_CODEX.md

scripts/
└── import_college_logos_batch2.py
```

Use the existing Next.js `public/` asset convention.
Do not create alternate parallel asset systems.

## Target asset naming

All imported assets must be renamed to the Evalio college slug:

```text
public/college-logos/university-of-southern-california.svg
public/college-logos/university-of-california-san-diego.svg
public/college-logos/university-of-texas-at-austin.svg
...
```

Frontend URL:

```text
/college-logos/university-of-southern-california.svg
```

## Codex implementation sequence

1. Inspect the current repo's `college_media` model, importers, and College UI surfaces.
2. Copy this manifest into `data/research/logo-batch2/college_logos_batch2.csv`.
3. Copy this README into `data/research/logo-batch2/README_CODEX.md`.
4. Copy the helper into `scripts/import_college_logos_batch2.py`.
5. Create `public/college-logos/` if needed.
6. Run the downloader for entries that have `asset_download_url`.
7. Validate each downloaded asset:
   - MIME is an image type (svg/png/jpeg/webp),
   - file is not empty,
   - not an HTML/login page,
   - renders correctly,
   - is an institutional mark rather than an athletics mark.
8. For entries marked `PENDING_OFFICIAL_DOWNLOAD`, leave the frontend on the Evalio fallback until a human or Codex obtains an approved official asset from the listed brand portal.
9. Generate/import `college_media` rows for the downloaded assets.
10. Point College cards and detail pages to `college_media` where `media_type = LOGO`.
11. Run tests, typecheck, lint, and build.
12. Stop before production deploy.

Example:

```bash
python scripts/import_college_logos_batch2.py   data/research/logo-batch2/college_logos_batch2.csv   --download   --write-media-csv
```

## Database mapping

Preferred `college_media` mapping:

```text
college_id        resolved from college_slug
media_type        LOGO
image_url         /college-logos/{slug}.{ext}
source_url        source_page_url
license           license_or_status
attribution       source_provenance
alt_text          "{school name} logo"
is_primary        true
verified_at       manifest verified_at
```

Recommended unique/upsert behavior:

```text
(college_id, media_type, image_url)
```

Re-running the import must be idempotent.

## Frontend behavior

- Use `logo?.image_url` when available.
- Use an Evalio branded initials fallback when no verified logo exists.
- Never show a broken image.
- Never hotlink external Wikimedia/brand URLs in production if a local verified copy exists.
- Never silently swap in an athletics mark.

Recommended container:
- `object-contain`
- height `48–64px`
- max-width `150–180px`
- no recoloring, stretching, cropping, or extra effects

## Legal / brand notes

Many simple wordmarks may be public-domain from a copyright perspective while still being trademark-protected.
Keep source, license/status, and trademark metadata.
Do not imply any university endorsement or partnership.

## Special notes by school

- **Emory / Boston College / Tufts / Boston University / UMD / UNC / Wake Forest / Virginia Tech / UCI / UC Davis / UF**:
  intentionally left pending for official-brand retrieval rather than risking the wrong mark.

- **UW–Madison / NYU / Ohio State / Texas A&M**:
  usable interim assets are included, but they should be revalidated against the current official brand portal before production.

- **University of Washington**:
  prefer the institutional signature, not the athletics block-W mark.

- **USC**:
  prefer the institutional university logo rather than athletics variants.

## Production gate checklist

```text
[ ] all downloaded files render correctly
[ ] no HTML/login pages were saved as images
[ ] Purdue maps to Purdue Main Campus identity
[ ] Texas A&M maps to Texas A&M University identity
[ ] no athletics logo accidentally used as the institutional logo
[ ] pending colleges still show Evalio fallback
[ ] college_media import is idempotent
[ ] tests / lint / build pass
```
