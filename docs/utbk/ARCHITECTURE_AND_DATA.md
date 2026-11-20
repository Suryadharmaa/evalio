# Evalio UTBK — Architecture, schemas and domain logic (draft)
Status: design proposal, NOT existing code.

## Existing foundation
Repository uses Next.js 16 + TypeScript/React 19 + Tailwind 4, Supabase Auth/PostgreSQL, separate FastAPI/Python 3.12, Vitest/Playwright. Existing international admission evaluation is independent. Keep current deploy working while adding /utbk.

## Proposed module boundaries
Frontend `app/utbk/`, `components/utbk/`, `lib/utbk/` -> typed API client only.
FastAPI `api/admission_engine/utbk/` or separate `api/utbk/` namespace following existing application composition, routes `/api/v1/utbk/*`. Do not extend scoring V1/V2 directly. Database migrations versioned via existing Alembic, verify current schema before creating.
Domain packages:
- catalog: PTN/program data, year-specific facts and provenance
- content: passages, questions, options, explanations, moderation, licensing
- exam: versioned blueprints, sessions, timer/submission state machine
- results: deterministic raw metrics, performance bands (clearly internal)
- entitlements: payment order, verified webhook, access grants
- reporting: issue flags, audit trails, data freshness

## Proposed key data entities (minimum fields)
`utbk_profiles`: user_id, exam_year, grade_or_alumni_status, created_at.
`subtests`: id, canonical_code, name; `topics`: id, subtest_id, parent_id, slug.
`questions`: id, subtest_id, topic_id, passage_id?, stem, question_type, difficulty, status, owner/license, author_id, reviewer_id, published_at, revision, source_ref, metadata.
`question_options`: id, question_id, label, content, display_order; correct answers stay server-restricted.
`question_explanations`: question_id, explanation, references, version.
`exam_blueprints`: id, year, version, duration_seconds, status, official_source_url, verified_at.
`blueprint_subtests`: blueprint_id, subtest_id, question_count, ordering_rule.
`exam_attempts`: id, user_id, blueprint_id, state, started_at, deadline_at, submitted_at, seed, version.
`attempt_items`: attempt_id, question_id, position, option_order_seed.
`attempt_answers`: attempt_id, question_id, selected_option_id, updated_at, unique(attempt_id,question_id).
`attempt_results`: attempt_id, correct_count, wrong_count, blank_count, per_subtest_json, scored_at, algorithm_version.
`institutions`: id, official_code, name, region, source, verified_at.
`programs`: id, institution_id, official_code, degree_level, faculty_name?, name.
`program_year_stats`: program_id, year, route, capacity?, applicants?, source_url, fetched_at, verified_at.
`student_shortlists`: user_id, program_id, exam_year, priority, notes.
`payment_orders`: id, user_id, provider, provider_ref, amount, currency, status, created_at, settled_at.
`entitlements`: user_id, product_key, begins_at, expires_at, status, payment_order_id.
`content_audit`: entity, entity_id, actor_id, action, before, after, timestamp.

## Data and access rules
- Public reads: published question stem/options only for authorized free/premium content; no correct-answer payload before a relevant submission or authorized review.
- RLS and API must enforce ownership for attempts, results, shortlists, and payments. Do not rely on frontend checks.
- Admin/reviewer role assignment occurs server-side, never a client-provided is_admin boolean.
- All data imports are staged and verified; missing stats remain NULL, not zero.
- Answer keys are not included in static export JSON or client JS bundles.
- Payment webhooks require signature validation, replay/idempotency handling and amount matching.
- Minimize minors' data; do not collect precise location, legal identity, or school name unless clearly necessary and consented.

## Tryout attempt state machine
`created -> in_progress -> submitted | expired | invalidated`; transitions are atomic and audited.
Server creates immutable question snapshot/selection, start time, deadline, and randomization seed.
Each answer upsert is scoped to the owner and rejected after closure; autosave is debounced client-side but server authoritative.
Submit accepts idempotency key; concurrent submit/expiry produce exactly one final result.
Timer display is derived from server deadline, not trusted as scoring authority.
Results compute exact raw correct/wrong/blank counts; show no official SNBT scaled score or passing-grade prediction.
If frontend offline: preserve unsent answer queue locally with clear 'not synced' warning; reconciliation rules documented and tested.

## Recommendation logic (non-ML MVP)
Per user and subtest/topic: compute attempts, accuracy (with sample-size warning), recent mistakes, and question recency. Recommend weakest topics with >= configured evidence threshold; if insufficient attempts, recommend balanced coverage. Do not infer admission probabilities.

## Design constraints
Reuse docs/evalio-DESIGN.md: deep purple #281950, accent #6757F5, backgrounds calm and neutral. Use original/licensed campus imagery sparingly in exploration/marketing; zero decorative clutter in test mode.
Use KaTeX for math after evaluating existing components; prefer built-in browser and current libraries for MVP.

## Key security/engineering tests
- Different user cannot read another attempt or entitlement.
- Anonymous user cannot download entire premium bank.
- Answer keys cannot be fetched before permitted review.
- Duplicate webhook cannot double-grant.
- Duplicate submit cannot rescore.
- Expired session cannot accept extra answers.
- Closing/reopening test preserves only server-synced state.
- Rules version changes do not retroactively change a completed attempt.
- 2026 legacy admissions tests still pass.

## Architectural open questions
Choose integrated FastAPI module vs independent UTBK service after examining route layout. Verify Supabase migration conventions and backend host capacity. Avoid inventing official 2027 rules and API access rights.
