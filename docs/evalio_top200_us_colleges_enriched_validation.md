# Evalio Top 200 enrichment validation

- Total institutions processed: 200
- Federal identity matches: 200
- Institutions fully enriched: 0
- Institutions with missing requested data: 200
- Testing policies: REQUIRED=25, OPTIONAL=159, FLEXIBLE=0, BLIND=16, UNKNOWN=0
- International aid policies: NEED_BLIND=8, NEED_AWARE=0, NO_NEED_BASED_AID=0, UNKNOWN=192
- Records with verified acceptance rate: 198
- Records with verified tuition and COA: 148
- Records requiring manual review: 192

## Manual review

- 192 institutions retain `UNKNOWN` international-aid policy; filter that column for institution-by-institution follow-up.
- 200 application fees remain blank because the federal release does not contain that field.
- SAT/ACT median columns remain blank; the available federal midpoint is derived rather than an institution-reported median.
- No duplicate, range, percentile-order, COA, or identity conflicts remain.

## Method note

Federal values are the latest available College Scorecard/IPEDS observations and are not relabeled as 2026-27 outcomes. Testing policy uses FairTest's 2026-27 database and its linked institution pages. International-aid fields remain `UNKNOWN` unless the input already carried stronger institution-specific evidence. Blank medians and application fees were intentionally not inferred. The original schema has no dedicated field for international first-year acceptance, so that attribute was not added.

## Sources

1. U.S. Department of Education, [College Scorecard dataset](https://catalog.data.gov/dataset/college-scorecard), May 2025 institution-level release — identity, admissions, testing percentiles, tuition, and annual cost fields.
2. U.S. Department of Education, [College Scorecard institution-level technical documentation](https://collegescorecard.ed.gov/files/InstitutionDataDocumentation.pdf), September 2025 — field definitions and cohort limitations.
3. FairTest, [Overview of Current Admission Testing Policies](https://fairtest.org/test-optional-list/), 2026-27 cycle — normalized required, optional, and test-free policies plus institution policy links.
