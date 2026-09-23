Implement Evalio College Logo Batch 1 from the provided package.

Read first:
- docs/DATA_SPEC.md
- docs/TECHNICAL_DESIGN.md
- docs/UI_UX_SPEC.md
- docs/evalio-DESIGN.md
- the package README_CODEX.md
- college_logos_batch1.csv

Rules:
- do not generate, redraw, recolor, or invent logos;
- do not use Google Images;
- do not silently substitute athletics marks;
- preserve source/license/trademark metadata;
- download only manifest-approved upstream assets;
- rename assets to Evalio slugs under public/college-logos/;
- use existing college_media schema/import flow where possible;
- no duplicate media rows;
- no production DB import automatically;
- Notre Dame must remain fallback/PENDING until an approved Primary Academic Mark is available;
- MEDIUM assets must keep their confidence/status metadata.

Tasks:
1. Inspect existing college_media model/importer/frontend.
2. Create missing folders only:
   public/college-logos/
   data/research/logo-batch1/
   scripts/ (only if not present)
3. Place the manifest/README in data/research/logo-batch1/.
4. Place/import the provided downloader as scripts/import_college_logos.py.
5. Run the downloader in local/staging.
6. Validate MIME, non-zero size, SVG/PNG rendering, and that downloads are not HTML/login pages.
7. Generate/upsert LOGO college_media rows using college slug -> college UUID resolution.
8. Wire College Explorer and college detail surfaces to college_media LOGO.
9. Use object-contain and an Evalio initials fallback when no verified logo exists.
10. Run tests, typecheck, lint, and production build.
11. Report downloaded assets, skipped/pending assets, media rows inserted/updated, and any branding conflicts.
12. Stop before production import/deploy.
