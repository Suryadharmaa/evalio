# Evalio College Research — Batch 1 Data Dictionary

Research as of: 2026-09-14

## Scope

Batch 1 is the **core 200-school research layer**. It normalizes identity, core admissions metrics,
2026–27 testing policy, testing bands, application fee where verified, tuition/COA baseline,
international-aid policy where already official-verified, source provenance, and research gaps.

It is intentionally source-aware: a blank value is better than an invented value.

## Important semantics

- `acceptance_rate_pct`: percentage from 0–100, not a fraction.
- `test_policy_2026_27`: REQUIRED / OPTIONAL / FLEXIBLE / BLIND / UNKNOWN.
- `international_aid_policy`: NEED_BLIND / NEED_AWARE / NO_NEED_BASED_AID / UNKNOWN.
- `international_need_based_aid`: YES / NO / UNKNOWN.
- `meets_full_demonstrated_need_international`: YES / NO / UNKNOWN.
- Blank numeric value: unavailable / not verified in this batch.
- `UNKNOWN`: categorical policy was not safely verifiable from the available source.
- `source_cycle`: the cycle/data vintage of the supporting source; never assume all columns share one cycle.
- `cost_basis`: describes whether cost is an OOS/IPEDS baseline or another published basis.

## Files

### colleges.csv
Canonical institution identity for 200 Evalio schools.

### admissions.csv
Core admissions/testing data, 2026–27 test policy, app fee where verified, and source links.

### financial_aid.csv
Tuition/COA baseline and international-aid policy status.

### sources.csv
Field-group provenance records.

### master_200_batch1.csv
Convenience wide export for inspection. Do not treat it as the preferred normalized production schema.

### research_gaps.csv
Every high/medium/low-priority missing field targeted for the next verification batch.

### identity_corrections.csv
Critical institution/campus binding errors fixed in Batch 1.

### college_media.csv
Previously verified campus media retained as-is.

### media_coverage.csv
Coverage status for campus media across all 200 institutions.

## Source hierarchy

1. Official institution admissions / financial-aid pages
2. School-published Common Data Set
3. NCES/IPEDS
4. U.S. Department of Education College Scorecard
5. Common App / official platform documentation
6. FairTest for 2026–27 testing-policy verification
7. CollegeData.fyi as a source-labeled archive/serving layer for CDS + federal facts

## Rule

Never fill a missing median SAT/ACT by averaging the 25th and 75th percentiles.
Never infer international need policy from domestic policy.
Never infer "meets full need" from the existence of need-based aid.
