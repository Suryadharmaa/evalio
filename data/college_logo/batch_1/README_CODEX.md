# Evalio College Logos — Batch 1 (#1–25)

**Purpose:** curated, source-backed logo manifest for the first 25 colleges in Evalio's 200-school seed.

This package does **not generate or redraw logos**. It identifies upstream institutional/brand assets and provides stable source/download references for Codex to place into the Evalio repository.

## Coverage

- 25 colleges reviewed.
- 24 have a downloadable candidate asset in the manifest.
- 1 (University of Notre Dame) is intentionally **PENDING_OFFICIAL_DOWNLOAD** because the current Primary Academic Mark download is access-controlled. Do not silently substitute the athletics monogram or university seal.
- Most entries use institutional wordmarks/logos rather than athletics marks.
- `verification_quality=MEDIUM` means the asset is useful as an interim implementation asset but should be revalidated against the institution's current brand portal before production.

## Required repository folders

Codex should create these only if they do not already exist:

```text
public/
└── college-logos/

data/
└── research/
    └── logo-batch1/
        ├── college_logos_batch1.csv
        └── README_CODEX.md

scripts/
└── import_college_logos.py
```

Do **not** create a parallel frontend asset system such as:

```text
assets-v2/
college-assets-new/
logos-final/
```

Use the existing Next.js `public/` convention.

## Target asset naming

Every local asset must be renamed to its Evalio college slug:

```text
public/college-logos/princeton-university.svg
public/college-logos/harvard-university.svg
public/college-logos/johns-hopkins-university.png
...
```

The frontend URL becomes:

```text
/college-logos/princeton-university.svg
```

Do not use the upstream filename in frontend code.

## Codex implementation sequence

1. Read the current repo and data specs before modifying anything.
2. Copy this manifest to `data/research/logo-batch1/college_logos_batch1.csv`.
3. Copy `import_college_logos.py` to `scripts/import_college_logos.py`.
4. Create `public/college-logos/`.
5. Run the downloader from repository root.
6. Verify every downloaded file:
   - non-zero bytes;
   - actual image MIME type;
   - SVG/PNG/JPEG only;
   - renders correctly;
   - not an HTML error/login page;
   - no athletic logo substituted for an institutional logo unless manifest explicitly says so.
7. Generate/import `college_media` rows.
8. Connect the frontend College cards/detail pages to `college_media` instead of hardcoded image mappings.
9. Use a branded Evalio fallback whenever no verified logo exists.
10. Do not hotlink Wikimedia/official-site assets in production if a verified local copy has been stored.

Example command:

```bash
python scripts/import_college_logos.py \
  data/research/logo-batch1/college_logos_batch1.csv \
  --download \
  --write-media-csv
```

## Database mapping

Preferred `college_media` representation:

```text
college_id        resolved from college_slug
media_type        LOGO
image_url         /college-logos/{slug}.{ext}
source_url        original source/provenance page
license           license_or_status from manifest
attribution       source_provenance
alt_text          "{school name} logo"
is_primary        true
verified_at       manifest verified_at
```

If the existing `college_media` schema also supports:

```text
width
height
sha256
content_type
```

populate them after downloading/inspection.

Do not add duplicate columns/tables if equivalent fields already exist.

## Upsert rule

Recommended key:

```text
(college_id, media_type, image_url)
```

or reuse the current canonical media upsert rule if one already exists.

Re-running the import must not create duplicate LOGO records.

## Frontend behavior

Use:

```tsx
logo?.image_url
```

when a verified `LOGO` media record exists.

If no logo exists:

```text
show Evalio branded fallback
school initials
```

Do not:

- show a broken `<img>`;
- hotlink a random Google image;
- use an athletics mark as a silent fallback;
- infer a filename from the college name;
- scrape the logo at runtime;
- make the browser contact Wikimedia directly for every render.

Suggested card presentation:

```text
[ logo container ]
School Name
Location
...
```

Logo container should use `object-contain`, not `object-cover`.

Recommended visual box:

```text
height: 48–64px
max-width: 150–180px
padding: 8–12px
background: white or transparent
```

Never recolor, crop, stretch, distort, or add effects to university logos.

## Legal / brand notes

Copyright status and trademark status are separate.

Many simple wordmarks on Wikimedia Commons are marked public domain because they do not meet the copyright threshold, while still being protected trademarks. Keep `source_url`, license/status, and trademark metadata.

Do not imply that any university endorses, sponsors, or partners with Evalio.

For institutional marks whose official brand portal restricts downloads or requires approval, retain a fallback until an approved asset is available.

## Special cases

### Rice University

The current official Rice Brand Guide confirms the university uses approved logos, lockups, wordmarks, and a shield. Official downloads are access-controlled for the Rice community / external users may need to request files. The manifest therefore uses a Wikimedia-hosted interim logo and marks it `MEDIUM`.

### University of Notre Dame

The current Notre Dame brand page says the **Primary Academic Mark** is the appropriate academic mark. Its downloads are access-controlled. Do not substitute the athletics monogram or official seal on Evalio College cards. Keep the Evalio fallback until an approved Primary Academic Mark is obtained.

### Washington University in St. Louis

The current WashU identity has undergone recent updates. The manifest's text-logo asset is `MEDIUM` confidence and should be compared against the current official WashU brand materials before production.

### Vanderbilt

The selected SVG is sourced to Vanderbilt's official brand site, but Wikimedia notes an SVG validity/embedded-raster issue. Codex should open/render the downloaded file. If rendering is unreliable, use the corresponding official-sourced PNG/wordmark instead and update the manifest rather than silently rewriting the SVG.

## Production gate

Before enabling these logos in production:

```text
[ ] all files render
[ ] source metadata retained
[ ] trademarks not presented as partnerships
[ ] no athletics logo accidentally used
[ ] current brand status checked for MEDIUM/PENDING entries
[ ] college_media import idempotent
[ ] frontend fallback works
[ ] build/typecheck/tests pass
```
