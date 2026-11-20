---
name: evalio-utbk-engine
description: Use when designing or implementing Evalio UTBK question bank, practice, exam attempts, timer, autosave or deterministic scoring. Do not use for generic UI or legacy US admissions.
---
# Evalio UTBK engine — domain skill
Read only `docs/utbk/ARCHITECTURE_AND_DATA.md` and the relevant paths for the assigned ticket. Preserve legacy admissions.

## Rules
- Use year/versioned exam blueprints and published, reviewed questions.
- Never call an LLM to score answers; deterministic testable score logic only.
- Official exam scaled score not known: return raw correct/wrong/blank, no fake passing grade or admission probability.
- Correct answers are stored/checked server-side; never ship keys in unauthenticated/static frontend.
- Attempt state: created -> in_progress -> submitted|expired|invalidated, transactional/idempotent.
- Server start/deadline are time authority; test skew, reconnect, duplicate submit, multiple tabs, stale autosave.
- Preserve original question/option snapshots or version references so historical attempts remain reproducible.
- Access to attempts/results scoped by verified user, entitlement checked for premium content.
- Keep migration backward-compatible unless expressly approved.
- Add narrowly scoped unit/integration tests before requesting review.

## Delivery
One task/PR, concise changed files, tests, security/copyright implications, remaining assumptions. Do not merge/deploy.
