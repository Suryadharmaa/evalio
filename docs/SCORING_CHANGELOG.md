# Scoring changelog

## Profile evidence mapping 1.1.0 — 2026-09-12

- Academic rigor coverage now recognizes only the five documented core-area groups.
- Saved founder activities require concrete responsibility language before founder evidence is credited.
- Honor academic relevance receives full credit only when its academic area matches the intended major; unrelated academic honors receive partial relevance.
- Application audit 1.1.0 no longer reports an empty requirement dataset as complete and now prioritizes unevaluated present materials after completeness issues.

## Saved-profile rigor evidence mapping — 2026-09-10

- Saved courses contribute rigor evidence only when the applicant also records the number of advanced courses available at their school.
- Core coverage uses distinct reported subject areas; highest-level coverage and major preparation use explicit course flags.
- If term-level progression cannot be established, the neutral `MIXED` band is used. Missing opportunity context produces limited-data output instead of an inferred rigor score.

## College rubric 1.1.0 — 2026-09-13

- Application Strength now applies the published CDS importance mapping to available Evalio component signals.
- Unknown/unavailable CDS factors are excluded and cap otherwise-high confidence at Medium.
- College and testing rule IDs are returned and persisted with the evaluation.
- Application Strength is no longer an alias for Academic Alignment.

## Engine 2.0.0 — 2026-09-10

- Initial deterministic academic, activity, honor, essay, LOR, college, financial, application-audit, and profile-strength rubrics.
- Added committed golden outputs for every calibration fixture family.
- Inputs and results retain engine/rubric versions when saved.

Golden files must only be regenerated after an intentional rubric/version change and reviewer approval.
