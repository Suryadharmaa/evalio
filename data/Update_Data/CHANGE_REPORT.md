# Evalio Data Refresh — 2026-09-20

## What was updated

This package updates the four CSVs supplied by the user **in this workspace**, not in Codex.

### `evalio_top200_us_colleges_enriched_UPDATED.csv`

- Preserves all 200 rows and the original 35-column schema.
- Merges the existing source-backed Batch 2A/2B research for schools #1–100.
- Fills application fees where Batch 2 already established a numeric current value.
- Replaces/refreshes current-cycle testing policy and source links for the first 100 where available.
- Enriches international financial-aid policy/source fields for the first 100 without converting `UNKNOWN` to `NO`.
- Refreshes current admissions metrics for the 12 core colleges using source-linked CDS / official CDS data.
- Refreshes 2026-27 tuition and COA for the same 12 from official university sources.

### `admissions_UPDATED.csv`

All 12 rows now have applicant/admit/enrolled totals and computed acceptance rates.
SAT/ACT percentiles are filled only when directly reported.
International applicant/admit counts remain blank unless a source explicitly labels them.

### `financial_aid_UPDATED.csv`

All 12 rows now have 2026-27:
- estimated cost of attendance
- tuition
- room + board
- books/personal estimate
- source-specific caveats in `notes`

### `colleges_UPDATED.csv`

The supplied 12-row identity file was already complete. It is preserved with no factual changes.

## Non-inference rules used

- Blank is not zero.
- `UNKNOWN` is not `NO`.
- SAT/ACT median is not inferred from P25 and P75.
- International applicant/admit counts are not inferred from unlabeled residency blocks.
- Variable travel/health-insurance costs are described in notes rather than invented into a universal fixed value.
- Aid categories from prior Batch 2 research are preserved with their nuance rather than flattened into a false boolean.

## Source policy

The companion `update_sources.csv` records the source URL, source type, academic cycle, and verification date for refreshed fields.

CollegeData.fyi is used only as a source-linked CDS archive where noted. Official university sources are preferred for current 2026-27 cost information.

## Remaining gaps

See `remaining_gaps.csv`.

The largest remaining gaps in the 200-school file are expected to be:
- SAT/ACT medians not directly published by many institutions
- second-half (#101–200) application-fee / international-aid verification
- some COA values
- international-specific applicant/admit counts

These remain blank intentionally rather than fabricated.
