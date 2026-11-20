# Evalio UTBK — Quality assurance and trust checklist

## Build quality
Use existing GitHub Actions .github/workflows/ci.yml to maintain baseline: lint, TypeScript, frontend tests, Playwright, Ruff, MyPy, backend coverage, migration SQL, dependency audits, build.
Run focused tests for a change, then full CI on PR. Never edit tests to hide a defect.

## Exam engine: must-pass properties
- Blueprint is year+version-bound; a finished attempt is immutable.
- Every exam question is drawn from published/licensed content.
- Randomized question/option ordering persists across reload; result mapping remains correct.
- Timer uses server deadline, rejects post-expiry submissions, handles client clock skew.
- Concurrent save, late save, double-click submit, duplicate HTTP requests, reconnect, and two tabs cannot corrupt scores.
- Partial submissions and timeout produce policy-consistent outcomes.
- Correct answer and explanations are not leaked before release policy allows it.
- Per-subtest totals reconcile with correct + incorrect + blank.
- Normalized "official" UTBK score and passing grade are never invented.

## PTN content: must-pass properties
- Data source, date and selection year visible for each number.
- Missing/suppressed data means unavailable, never 0.
- Outdated 2026 rules not presented as binding 2027 rules.
- School/accreditation/UKT claims require a dated primary source.
- No implication of government/PTN endorsement.
- Program identifiers must be stable; renamed/merged prodi carry effective dates.

## Financial & security
- Data scoped by user ID for attempts, orders, profile and shortlist.
- Premium checks enforced server-side; answer keys not sent in public static assets.
- Payment signature verified server-side, currency/amount/provider reference matched, webhook replay idempotent; delayed callback handled.
- No private user data in analytics, debug screenshots, Codex prompts or CI logs.
- Deletion/export process documented and tested; protect child/minor personal data.
- Abuse controls: rate limits, question scraping mitigation, pagination/quotas and server-side entitlement.

## Content QA process
1. Author or ingest from licensed partner with source/rights field.
2. Independently check stem/options and unambiguous correct answer.
3. Validate mathematical expressions/rendering and language clarity.
4. Assign subtest, topic, difficulty and rubric tags.
5. Reviewer approves; version increments on edits; old attempts still reproducible.
6. Publish to limited group, log reported mistakes, retire defective versions.

## Pilot testing
Device matrix: Android Chrome budget phone, iPhone Safari, desktop Chrome/Firefox; slow cellular and reconnect. Test one assistive technology path, mobile landscape, keyboard-only, reduced motion. Ask pilot students to perform without assistance: diagnostic, practice correction, timed tryout, PTN shortlist. Collect anonymous pain points and explicit consent if telemetry is collected.
