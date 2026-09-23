Implement Evalio College Logo Batch 2 from the provided package.

Read first:
- docs/DATA_SPEC.md
- docs/TECHNICAL_DESIGN.md
- docs/UI_UX_SPEC.md
- docs/evalio-DESIGN.md
- the package README_CODEX.md
- college_logos_batch2.csv

Rules:
- do not generate, redraw, recolor, or invent logos;
- do not use Google Images;
- do not silently substitute athletics marks;
- preserve source/license/trademark metadata;
- download only manifest-approved upstream assets;
- rename assets to Evalio slugs under public/college-logos/;
- use the existing college_media schema/import path where possible;
- do not auto-deploy to production.

Critical identity rules:
- `purdue-university` must resolve to Purdue University (Main Campus / West Lafayette), not Purdue University Global.
- `texas-a-and-m-university` must resolve to Texas A&M University, not West Texas A & M University.

Tasks:
1. Inspect the current college_media model/importer/frontend usage.
2. Create missing folders only:
   - public/college-logos/
   - data/research/logo-batch2/
   - scripts/ (only if missing)
3. Place the provided manifest + README in `data/research/logo-batch2/`.
4. Place the provided importer in `scripts/import_college_logos_batch2.py`.
5. Download and validate only entries with a ready `asset_download_url`.
6. For `PENDING_OFFICIAL_DOWNLOAD` entries:
   - do not fabricate a replacement;
   - keep the Evalio fallback;
   - optionally log a TODO list for manual brand retrieval.
7. Generate/upsert LOGO rows into college_media.
8. Wire College Explorer and college detail surfaces to use LOGO media records.
9. Keep UI resilient when a school has no verified logo.
10. Run tests, typecheck, lint, and production build.
11. Report:
   - assets downloaded,
   - assets skipped/pending,
   - assets that failed validation,
   - media rows inserted/updated,
   - any slug/identity mismatches found.
12. Stop before production deployment.
