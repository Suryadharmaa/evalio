# Evalio College Research Batch 1

This package upgrades the original Evalio seed data from a small 12-school seed into a normalized
200-school research baseline.

## What changed

- 200 canonical institutions
- core admissions/testing data carried forward from the researched 200-school baseline
- 2026–27 test-policy values retained with provenance
- tuition/COA baseline normalized
- source provenance expanded
- gaps made explicit rather than silently guessed
- four critical wrong-campus/institution matches corrected
- existing licensed campus-media records preserved

## Recommended use

1. Review `VALIDATION_REPORT.md`.
2. Review `identity_corrections.csv`.
3. Use `master_200_batch1.csv` for human inspection.
4. Use normalized `colleges.csv`, `admissions.csv`, `financial_aid.csv`, and `sources.csv` for Codex/database integration.
5. Do not import `research_gaps.csv` as facts; it is the next-research queue.
6. Run a staging/dry-run import before production.

## Batch 2 target

Deep official-source verification for all 200:

- international need policy
- meets-full-need commitment
- CSS Profile / ISFAA / institutional forms
- application fee
- ED / EA / REA / RD policies and deadlines
- English proficiency tests and minimums
- counselor / teacher recommendation requirements
- essays / supplements / interview
- official website and admissions URLs
- current annual international/OOS cost
- campus media licensing

## Research principles

Accuracy > completion.
A blank field is preferable to a fabricated value.
UNKNOWN must not be interpreted as NO.
