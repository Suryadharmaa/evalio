Implement Evalio College Logo Batch 3 from the provided package.

Read:
- docs/DATA_SPEC.md
- docs/TECHNICAL_DESIGN.md
- docs/UI_UX_SPEC.md
- docs/evalio-DESIGN.md
- data/research/logo-batch3/README_CODEX.md
- data/research/logo-batch3/college_logos_batch3.csv

Non-negotiable:
- do not generate or redraw logos;
- do not use image-search results as production assets;
- do not silently use athletics marks;
- preserve source/license/trademark metadata;
- use local files under public/college-logos/;
- reuse the existing college_media model/import system;
- do not auto-deploy or import to production.

CRITICAL IDENTITY:
`north-carolina-state-university` is NC State University at Raleigh, NOT North Carolina A&T State University.

Tasks:
1. Inspect current models/importers/UI.
2. Create only missing folders:
   public/college-logos/
   data/research/logo-batch3/
   scripts/
3. Place manifest + README in data/research/logo-batch3/.
4. Place helper script in scripts/import_college_logos_batch3.py.
5. Download only manifest entries that have asset_download_url.
6. Validate MIME, non-zero size, renderability, and correct institution identity.
7. Do not attempt to bypass access-controlled brand portals.
8. Leave pending schools on the Evalio initials fallback.
9. Generate/upsert college_media rows with media_type=LOGO.
10. Wire College Explorer/detail pages to media records rather than hardcoded logo maps.
11. Use object-contain and preserve original proportions/colors.
12. Run tests, lint, typecheck, and production build.
13. Report downloaded, pending, failed, inserted/updated, and identity conflicts.
14. Stop before production deployment.
