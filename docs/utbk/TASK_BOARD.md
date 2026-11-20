# Evalio UTBK — Ordered engineering task board
Each ticket is ONE bounded Codex Cloud task/PR unless review approves grouping. Dependencies must be met; do not begin external payment/service integration before internal test gates.

| ID | Stage | Task / scope | Acceptance / exit criteria | Dependencies |
|---|---|---|---|---|
| EVAL-001 | 0 | Audit current routes, API composition, migrations, components, CI | Architecture map + risks only; no production code changed | None |
| EVAL-002 | 0 | Finalize school pilot test + pricing survey | Anonymized findings and 3 purchase questions; no student private details | None |
| EVAL-003 | 1 | Add UTBK route skeleton /utbk and nav entry | Old routes unchanged; responsive empty/loaded/error states; focused tests | 001 |
| EVAL-004 | 1 | UI design tokens and reusable exam components | Mobile keyboard/touch tested; match existing Evalio identity | 001,003 |
| EVAL-005 | 1 | Blueprint/subtest versioned schema and seed 2026 baseline | Migration reversible; sources tracked; 2027 not claimed official | 001 |
| EVAL-006 | 1 | Questions/options/explanations/passages + moderation schema | Correct answer server-only; licensing/reviewer fields; RLS tests | 005 |
| EVAL-007 | 1 | Import/review pipeline for original questions | Draft -> review -> published; invalid items rejected; audit trail | 006 |
| EVAL-008 | 2 | Practice session API and UI | Access-controlled item delivery, answer feedback after submit, recovery | 006,004 |
| EVAL-009 | 2 | Diagnostic prototype | All seven subtests represented; no official scoring claim | 008 |
| EVAL-010 | 2 | Timed tryout attempt state machine/API | Double submits/time expiry idempotent; ownership tests | 005,006 |
| EVAL-011 | 2 | Tryout UI timer/palette/autosave | 360px mobile responsive, reconnect, no distracting popups | 010,004 |
| EVAL-012 | 2 | Deterministic raw-scoring and per-subtest results | Pure unit tests; no unofficial admission probability | 010 |
| EVAL-013 | 2 | Study dashboard and weak-topic hints | Clear sample-size warnings; no AI required | 008,012 |
| EVAL-014 | 3 | PTN/program model with dated historical facts | Nullable missing stats, source/year/verified field, permission review | 001 |
| EVAL-015 | 3 | PTN explorer / source panel / comparison UI | Filters and citations, no missing=0 bug, accessible mobile | 014,004 |
| EVAL-016 | 3 | Shortlist and year-specific rule validation | User-scoped saved choices; 2027 policy disabled until verified | 015 |
| EVAL-017 | 4 | Closed beta content QA and instrumentation | Tests and user research; >0 corrected items tracked | 009,011,015 |
| EVAL-018 | 4 | Dev payment provider with verified webhook and entitlement | Sandbox only, signature + idempotency + access tests | 017 |
| EVAL-019 | 4 | Privacy/deletion/retention review, load/security testing | 0 open critical issues, source/privacy documentation | 018 |
| EVAL-020 | 5 | Production readiness review and gradual rollout | Founder signoff, complete CI, rollback and incident runbook | 019 |

## Suggested milestone ordering
M0 documentation + cloud readiness; M1 designs + content models; M2 practice/diagnostic; M3 secure tryout; M4 PTN explorer/planner; M5 closed beta; M6 paid launch if evidence supports it.
Do NOT commit to fixed dates until engineering velocity, content rights, and school calendar are confirmed.

## Task acceptance template
**Goal:** one user-facing behavior. **Scope:** explicit paths/modules. **Out of scope:** adjacent refactor, payment, production deployment. **Tests:** exact commands and expected scenarios. **Output:** PR link + changed files + tests + risks + next blocker.

## Escalation
Any change to payment, production database, official rules, user privacy, third-party copyright, migration destructive changes, or `main` requires founder approval before execution.
