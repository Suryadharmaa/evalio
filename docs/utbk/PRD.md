# Evalio UTBK-SNBT 2027 — Product Requirements Document
Version: 1.0 draft | Date: 2026-11-20 | Status: For founder review
Product owner: Evalio founder | Engineering: Codex Cloud-assisted

## 1. Executive summary
Evalio UTBK is an affordable, mobile-first exam-preparation and Indonesian public-university planning web module for Class 12 SMA/SMK/MA students and eligible alumni. It extends the existing Evalio admissions product rather than replacing it. Promise: *Latihan terarah, keputusan PTN lebih terencana*.

**Validation:** Founder reports informal conversations with ~20–23 classmates who wanted affordable study resources. This is qualitative discovery, not purchase validation. Paid willingness, frequency, and pricing need further testing.

## 2. Problem / user / jobs to be done
Students struggle to find affordable, trustworthy, organized practice across all UTBK subtests, useful explanations, consistent progress tracking, and grounded PTN/prodi comparison. Students should be able to:
- Determine starting strengths and weaknesses through a diagnostic test.
- Practice by subtest/topic/difficulty and understand mistakes.
- Take timed tryouts with reliable saving, scoring, and review.
- Search PTNs/programs, compare authoritative historical data, and shortlist feasible options.
- Pay an optional transparent, affordable season pass if premium value is clear.

Primary persona: Indonesian student in Grade 12, phone-first, limited budget, intermittent connectivity. Secondary: gap-year / eligible applicant. Tertiary: content reviewer and admin.

## 3. Product principles and non-negotiables
1. Accurate and traceable: display source, year, revision date for admission facts.
2. Practice score != official UTBK result. No guarantee of admission or fabricated official passing grade.
3. 2026 SNBT format is a baseline **until official 2027 rules are verified**. Store exam configuration by year/version, never hardcode 2027 policy.
4. Use original/licensed questions only; citations do not grant redistribution rights. Editorial QA before publishing; AI drafts cannot auto-publish.
5. Test modes are distraction-free and accessible, usable on mobile.
6. Minimize personal data; no public student leaderboards by default. Minors' data require appropriate privacy and consent safeguards.
7. Separate all UTBK logic from the existing international admissions scoring engine.

## 4. Supported exam coverage baseline (official 2026, pending 2027)
Seven subtests: Penalaran Umum (30), Pengetahuan dan Pemahaman Umum (20), Pemahaman Bacaan dan Menulis (20), Pengetahuan Kuantitatif (20), Literasi Bahasa Indonesia (30), Literasi Bahasa Inggris (20), Penalaran Matematika (20). Total baseline 160 questions, 195 minutes. Store `exam_blueprints` and `blueprint_subtests` with source URL and effective year. No claim the 2027 structure is confirmed.

## 5. MVP P0 (must ship before initial paid beta)
F01 Accounts and profile: optional browsing; email sign-in; target exam year; target PTNs/programs; account data export/deletion pathway.
F02 Question library: seven subtests with accessible reading passages and math markup; topic filters; explanation, provenance, difficulty and review status.
F03 Practice: session per topic/subtest, save answer and bookmark, explanation after submission, retry incorrect items.
F04 Diagnostic: short representative set across seven subtests; clear non-official topic-level feedback; sufficient items to avoid false precision.
F05 Tryout: configurable blueprint, timer, next/previous/flag, confirmation before submission; autosave server-side; resume policy documented; server is authoritative for submission time.
F06 Results: raw correct/incorrect/omitted counts by subtest, weak-topic recommendations, progress across attempts; never fake official scaled UTBK score.
F07 PTN Explorer: source-backed list of PTNs and programs, degree level, location, 2026 historical capacity/demand where valid, source links and freshness.
F08 PTN shortlist: save and compare programs, show verified policy constraints *only once confirmed* for a selected admissions year.
F09 Admin content and rules: role-gated creation/import/review/version/publish/retire, change history and audit log.
F10 Freemium entitlement: free diagnostic/limited practice; premium access policies, checkout through Indonesian payment provider, signed webhook + idempotency, refunds handled per published policy.
F11 Operations: observability, rate limiting, RLS/authorization, content entitlement checks, backup and incident procedures.

## 6. P1 and P2 (not MVP)
P1: adaptive daily plan, weekly progress, smart recommendations from deterministic item metadata, richer charts, question issue reporting. P2: opt-in AI explanations with human-quality guardrails, school cohorts, community features, PWA offline packs where licensing allows. No real-time AI inference required for MVP.

## 7. Screens / jobs
- /utbk: marketing/overview and CTA to diagnostic.
- /utbk/onboarding: set year and initial target, start quickly.
- /utbk/dashboard: what to study today and recent progress.
- /utbk/practice: solve filtered questions without distractions.
- /utbk/tryout/[id]: full timed exam; minimal controls and reliable autosave.
- /utbk/results/[attemptId]: explain mistakes and recommend next practice.
- /utbk/ptn: find and compare universities and programs.
- /utbk/planner: shortlist, show data uncertainty and application rules.
- /utbk/billing: plans, entitlement, receipts.
- /admin/utbk: reviewer workflow, gated by explicit role.

## 8. Key flows / acceptance criteria
A. New student -> land -> optional account -> 15–25 minute diagnostic -> sees topic feedback and first recommended practice. Meets WCAG-aware keyboard/touch usability and no ungrounded admission percentage.
B. Practice -> question displayed -> answer -> submit -> correct answer + reviewed explanation -> recorded history. Reload cannot duplicate attempt.
C. Tryout -> start -> answer / flag / navigate -> server autosave -> submit or time expiry -> one immutable result. A retry, duplicate request, network outage, multi-tab, and expired session cannot create an inconsistent result.
D. PTN -> select year -> filter -> view program with source date and coverage warnings -> shortlist. Stale/missing numbers show 'Data belum tersedia', never 0.
E. Premium -> checkout -> verified server webhook -> entitlement active, with idempotency. Frontend never grants premium based only on redirect or local storage.
F. Admin -> draft -> peer review -> publish -> version / retire, with editor identity and source/licensing fields.

## 9. Pricing hypothesis, not validated
Free: sampling, diagnostic, selected PTN explorer. Test Student monthly IDR 19,000 / 30 days and season pass IDR 69,000 until the defined end of SNBT 2027 cycle. Conduct willingness-to-pay test before committing. Show transparent taxes/fees/expiry; no automatic renewal by default for seasonal purchase.

## 10. Success metrics / decision gates (targets to validate)
Discovery: 30 additional interviews across schools; >=10 follow-up users complete a supervised prototype session. Beta: >=70% of invited users can finish diagnostic without assistance; >=95% sample QA tests correct; 0 critical privacy/payment bugs; tryout session completion is measured, not assumed. Commercial: at least 10 real voluntary paid purchases from unrelated customers before scaling spend. Treat all numeric thresholds as provisional product goals.

## 11. Data governance / content provenance
Questions store ownership/license, author, reviewed_by, reviewed_at, source_reference, question_version, subtest/topic, correct answer stored on protected server, and status draft/review/published/retired. No mass reproduction of third-party paywalled/copyrighted material. Historical campus facts store source_url, retrieval_date, source_year, publication year and validation status.

## 12. Non-functional requirements
P0: mobile-first responsive design; readable Indonesian copy; secure auth and role-scoped row access; protect answers/entitlements server-side; idempotent submission and webhook; recoverable drafts; per-feature telemetry without sensitive text; analytics opt-in where necessary. Performance budgets and uptime targets will be measured during beta rather than claimed.

## 13. Dependencies / open decisions
D1 Check and update 2027 SNPMB blueprint when issued.
D2 Confirm rights/license and editorial capacity for initial 800–1,000 original/reviewed items (aspiration, not a launch promise).
D3 Confirm PTN data reuse/API rights and maintenance budget.
D4 Validate pricing with pilot and budget for gateway fees/chargebacks.
D5 Confirm hosting strategy for dynamic content given existing static GitHub Pages + separate FastAPI.
D6 Define safe treatment of student/minor personal data, retention, deletion and consent based on applicable law.

## 14. Launch definition
An invited student can sign in, complete practice + a timed mock, review results, research a source-backed PTN, save a shortlist, and (for selected testers) purchase safely. A QA reviewer can publish corrected questions without redeploying frontend. Existing Evalio admissions functionality and CI must remain green.

## 15. Reference sources (checked 2026-11-20)
- SNPMB general rules: https://www.snpmb.id/utbk-snbt/informasi-umum
- SNPMB exam framework: https://snpmb.id/fr/
- SNPMB program capacity: https://www.snpmb.id/utbk-snbt/daya-tampung-snbt
- Existing repository: https://github.com/Suryadharmaa/evalio
- Existing docs: docs/PRD.md and docs/evalio-DESIGN.md
