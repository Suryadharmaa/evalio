---
name: evalio-ptn-data
description: Use when building Evalio Indonesian PTN/prodi catalog, historical admissions statistics, source provenance, comparison or SNBT selection validation.
---
# Evalio PTN facts — domain skill
Read `docs/utbk/PRD.md` and `docs/utbk/ARCHITECTURE_AND_DATA.md` on demand.

## Rules
- Prefer primary sources: SNPMB, official PTN sites, PDDikti, with source URLs, year, retrieved/verified date.
- Treat 2026 rules as historical reference, not binding 2027 policy until official verification.
- Store nullable missing data, never substitute zero for unknown and never invent score thresholds.
- Distinguish historical competitiveness from a student's admission probability.
- Verify commercial reuse/API permissions before automating ingestion; avoid scraping copyrighted/paywalled material.
- Model effective dates/changes in program identifiers and names.
- Ensure shortlist is private and access-controlled. Keep query performance and mobile filters in mind.
- Test rule versions, missing sources, outdated data, renamed programs, and user ownership.

## Delivery
One source-backed feature per PR, explicit uncertainties and stale data flags. No production data write without approval.
