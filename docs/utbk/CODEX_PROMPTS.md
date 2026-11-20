# Codex Cloud task prompts — Copy/paste pack
Before each prompt choose GitHub repo `Suryadharmaa/evalio`, an approved Codex Cloud environment, and a task branch. Prefer GPT-6.1 Sol Medium if available. These are bounded prompts, not permission to deploy or merge.

## Prompt 0 — read-only audit
You are engineering Evalio UTBK in Codex Cloud. Read AGENTS.md, docs/utbk/README.md, docs/utbk/PRD.md, and docs/utbk/ARCHITECTURE_AND_DATA.md. Investigate only existing route structure, FastAPI composition, migrations, authentication, current UI library, and CI relevant to EVAL-001. Do not modify production files. Produce concise architecture map, important reusable modules, likely migration paths, security concerns, and small PR plan. Cite exact repo paths. No package installation unless needed to inspect existing code.

## Prompt 1 — landing and route skeleton
Implement only EVAL-003. Read AGENTS.md, docs/utbk/PRD.md and docs/utbk/DESIGN_SYSTEM.md; inspect only affected route and components. Build mobile-first /utbk route and lightweight nav entry following existing Evalio identity. UI should be in Indonesian and use a neutral placeholder instead of unlicensed campus assets. Do not modify legacy admissions scoring, production API, database or billing. Add targeted tests and run them. Provide concise diff and PR. Do not merge.

## Prompt 2 — question schema
Implement only EVAL-005 (not EVAL-006). Read docs/utbk/ARCHITECTURE_AND_DATA.md and current migration conventions. Propose then implement a versioned exam blueprint/subtest migration and a deterministic fixture for **2026** reference format; do not label it official 2027. Add migration tests and source metadata. Avoid destructive operations. Do not deploy to production. Show schema diff, tests, and PR.

## Prompt 3 — practice engine
Implement only EVAL-008 after dependencies exist. Read docs/utbk/ARCHITECTURE_AND_DATA.md and scoped skill evalio-utbk-engine. Build secure question delivery and practice answer submission with owner checks, with correct answers revealed only after submission. Include invalid item, anonymous, premium, repeat submission and reconnect test cases. Do not fetch arbitrary internet questions or use LLM scoring. Run focused tests; open PR.

## Prompt 4 — PTN catalog
Implement only EVAL-014. Read docs/utbk/ARCHITECTURE_AND_DATA.md, docs/utbk/PRD.md, scoped PTN skill. Add schema and fixtures for historically dated institution/program facts (2026 where verified), source URL, verified timestamp, nullable capacity/demand, revision. No unlicensed bulk data scrape, no admissions probability, no official 2027 rules. Tests and PR only.

## Prompt 5 — readiness review
Do not add features. Audit EVAL-010/011/012 for deterministic scoring, idempotency, time race, answer leakage, auth, RLS and mobile accessibility. Run relevant checks, document unrun tests. Report blockers by severity and propose smallest fixes. Never push production changes.

## Standard final response format
- Ticket and PR URL
- Scope and exact files changed
- Test commands and actual results
- Data/privacy/security issues
- Anything unverified
- Next smallest dependent ticket
