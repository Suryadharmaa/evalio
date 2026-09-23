# Evalio College Logos — Batch 3 (#51–75)

This package contains a curated logo manifest for Evalio colleges #51–75.

No logo in this package is generated or redrawn.

## Coverage

- 25 institutions reviewed.
- 15 manifest entries have download-ready institutional assets.
- 10 entries remain `PENDING_OFFICIAL_DOWNLOAD` because the current official brand system is restricted, access-controlled, or safer than using a questionable Commons/athletics asset.
- The package intentionally prefers **no logo + Evalio fallback** over a wrong logo.

## Critical identity correction

`north-carolina-state-university` must resolve to:

```text
North Carolina State University at Raleigh
```

not:

```text
North Carolina A&T State University
```

Do not import any NC A&T mark for this slug.

## Required repo folders

Create only if missing:

```text
public/
└── college-logos/

data/
└── research/
    └── logo-batch3/
        ├── college_logos_batch3.csv
        └── README_CODEX.md

scripts/
└── import_college_logos_batch3.py
```

Do not create parallel folders such as:

```text
logos-v2/
assets-new/
college-branding-final/
```

## Local naming

All local assets are renamed to the canonical Evalio slug:

```text
public/college-logos/florida-state-university.svg
public/college-logos/case-western-reserve-university.svg
public/college-logos/university-of-miami.svg
...
```

Frontend URLs:

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
   - `college_logos_batch3.csv`
2. Inspect the existing `college_media` schema/importer and current College Explorer/detail components.
3. Copy the manifest into `data/research/logo-batch3/`.
4. Put `import_college_logos_batch3.py` in `scripts/`.
5. Create `public/college-logos/` if needed.
6. Download only entries with a nonblank `asset_download_url`.
7. Validate:
   - file is non-empty;
   - MIME is SVG/PNG/JPEG/WebP;
   - not HTML or a login page;
   - image renders;
   - institution identity matches the slug;
   - mark is institutional, not athletics, unless explicitly documented.
8. For `PENDING_OFFICIAL_DOWNLOAD`:
   - do not invent a replacement;
   - do not scrape random image search results;
   - retain the Evalio initials fallback.
9. Generate/upsert `college_media` rows.
10. Wire College Explorer and college detail pages to query `media_type=LOGO`.
11. Run frontend/backend tests, lint, typecheck, and build.
12. Stop before production deploy/import unless separately instructed.

Example:

```bash
python scripts/import_college_logos_batch3.py   data/research/logo-batch3/college_logos_batch3.csv   --download   --write-media-csv
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

Reuse existing equivalent fields instead of adding duplicates.

Recommended upsert key:

```text
(college_id, media_type, image_url)
```

## UI behavior

College-card logo area should:

- use `object-contain`;
- preserve logo proportions;
- use a white/neutral background;
- not crop or stretch the mark;
- not recolor institutional logos;
- display a deterministic Evalio initials fallback when no logo exists.

Do not hotlink upstream logos in production if a local verified copy has been imported.

## Important school-specific notes

### University of Minnesota

UMN announced a refreshed brand site and updated primary/campus wordmarks in September 2026. Its official logo download is access-controlled. Keep it pending rather than importing an older wordmark as though it were current.

### Clemson

Clemson explicitly instructs users to use approved logo artwork and says generative AI must not create/redraw/alter its logos. This package intentionally leaves Clemson pending for approved artwork.

### William & Mary

The official Brand Hub exposes current university marks through Canto; use the approved primary logo rather than the outdated athletics marks commonly found elsewhere.

### Syracuse

The current Brand Toolkit requires NetID. Keep the Evalio fallback until a current approved asset is available.

### NC State

The upstream seed had a critical fuzzy-match error. The logo in this batch belongs to **NC State University at Raleigh**, which is the corrected institution for this Evalio slug.

## Production gate

```text
[ ] all downloaded assets render correctly
[ ] source/license metadata preserved
[ ] NC State identity correction verified
[ ] no athletics mark silently substituted
[ ] pending schools still use Evalio fallback
[ ] no logo implies university endorsement/partnership
[ ] college_media import is idempotent
[ ] lint/typecheck/tests/build pass
```
