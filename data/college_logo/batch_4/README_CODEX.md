# Evalio College Logos — Batch 4 (#76–100)

This package contains the logo manifest for Evalio colleges #76–100.

No logo in this package is generated or redrawn.

## Coverage

- 25 institutions reviewed.
- 16 entries have download-ready institutional assets in the manifest.
- 9 entries remain `PENDING_OFFICIAL_DOWNLOAD` because the safest source is the official university brand system, or because athletics/logo ambiguity makes a direct external derivative risky.
- The package prefers **verified institutional mark or Evalio fallback** — never a guessed replacement.

## Critical identity correction

`arizona-state-university` must resolve to:

```text
Arizona State University Campus Immersion
```

with the main Tempe/institutional identity, **not**:

```text
Arizona State University-West
```

This correction comes from the earlier Evalio identity-correction work. Do not attach a logo for the wrong campus/institution record.

## Required repo folders

Create only if missing:

```text
public/
└── college-logos/

data/
└── research/
    └── logo-batch4/
        ├── college_logos_batch4.csv
        └── README_CODEX.md

scripts/
└── import_college_logos_batch4.py
```

Do not create parallel folders like:

```text
logos-final-v4/
brand-assets-2026/
college-icons-new/
```

Use the existing Next.js `public/` convention.

## Local asset naming

Every imported logo must be renamed to the canonical Evalio slug:

```text
public/college-logos/baylor-university.svg
public/college-logos/fordham-university.svg
public/college-logos/arizona-state-university.svg
...
```

Frontend URL:

```text
/college-logos/{slug}.{ext}
```

## Codex implementation flow

1. Read:
   - `docs/DATA_SPEC.md`
   - `docs/TECHNICAL_DESIGN.md`
   - `docs/UI_UX_SPEC.md`
   - `docs/evalio-DESIGN.md`
   - this README
   - `college_logos_batch4.csv`
2. Inspect current `college_media` schema/importers and the College Explorer/detail UI.
3. Copy the manifest to `data/research/logo-batch4/`.
4. Put `import_college_logos_batch4.py` into `scripts/`.
5. Create `public/college-logos/` if it does not exist.
6. Download only entries with nonblank `asset_download_url`.
7. Validate:
   - non-empty file;
   - MIME type is SVG/PNG/JPEG/WebP;
   - download is not an HTML or login page;
   - image renders correctly;
   - correct institutional identity matches the slug;
   - mark is institutional, not athletics, unless explicitly documented.
8. For `PENDING_OFFICIAL_DOWNLOAD` entries:
   - do not invent a replacement;
   - do not scrape random Google/image-search results;
   - keep the Evalio initials fallback.
9. Generate/upsert `college_media` rows with `media_type=LOGO`.
10. Wire College Explorer and college detail pages to `college_media` rather than hardcoded logo maps.
11. Run tests, lint, typecheck, and production build.
12. Stop before production deploy/import unless separately instructed.

Example:

```bash
python scripts/import_college_logos_batch4.py   data/research/logo-batch4/college_logos_batch4.csv   --download   --write-media-csv
```

## Database mapping

```text
college_id      resolved by canonical college_slug
media_type      LOGO
image_url       /college-logos/{slug}.{ext}
source_url      source_page_url
license         license_or_status
attribution     source_provenance
alt_text        school logo alt text
is_primary      true
verified_at     manifest verified_at
```

Reuse existing equivalent fields instead of adding duplicate schema.

Recommended upsert key:

```text
(college_id, media_type, image_url)
```

## UI behavior

The college-card logo area should:

- use `object-contain`;
- preserve proportions;
- use a neutral/white background;
- not recolor or distort university marks;
- display a deterministic Evalio initials fallback when no verified logo exists.

Do not hotlink upstream logo URLs in production if a local verified copy has been imported.

## Important school-specific notes

### Arizona State University

The upstream seed previously pointed to Arizona State University-West. This package corrects the identity to the main Arizona State University / Campus Immersion record while preserving the existing Evalio slug.

### University of Oregon

Keep pending unless the current official institutional logo system is pulled from the official communications/brand source. Do not default to the athletics-only Oregon “O”.

### Auburn / Tennessee / Pepperdine / American / TCU / WPI

These are deliberately left pending when the safest route is the current official brand system rather than a questionable derivative file.

## Production gate

```text
[ ] all downloaded assets render correctly
[ ] source/license metadata preserved
[ ] Arizona State identity correction verified
[ ] no athletics marks silently substituted
[ ] pending schools still use Evalio fallback
[ ] no logo implies university endorsement/partnership
[ ] college_media import is idempotent
[ ] lint/typecheck/tests/build pass
```
