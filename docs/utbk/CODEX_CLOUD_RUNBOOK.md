# Codex Cloud implementation runbook — Evalio UTBK
Version 1.0 draft | 2026-11-20 | Target: GPT-6.1 Sol / Medium (when available)

## What 'cloud-only' means
Use an OpenAI-managed Codex Cloud environment attached to `Suryadharmaa/evalio`. Coding, npm/uv install, tests and git work occur in the remote workspace. No requirement to install Node, Python, Docker, Codex CLI or skills on the founder's laptop. A phone/browser can submit tasks after the cloud environment has been configured through a supported web/desktop interface. Do not confuse Codex *execution environment* with production hosting.

Official overview: https://help.openai.com/en/articles/20001545-using-codex-cloud

## Cloud setup — owner action once
1. Open Codex on supported web or desktop and authorize GitHub for `Suryadharmaa/evalio`; grant minimum repository permissions.
2. Create a reusable cloud environment for this repository, base branch `main` (or the accepted documentation branch while bootstrapping).
3. Choose a Linux image with Node.js >=20.9 (prefer Node 22 LTS), npm, Python 3.12 and `uv` (the repo README requirements), or configure them with the environment's supported package setup.
4. Add setup command: `bash scripts/codex-cloud-setup.sh` **after this branch is merged or in the bootstrap branch**. This runs `npm ci` and `uv sync --frozen`. Run setup in the environment, not on user's device.
5. Configure internet egress for setup only if required: npm registry, Python package index, GitHub release endpoints and browser-install hosts as dictated by allowed network policy. Prefer pinning package versions/lockfiles. Keep agent runtime network restricted where possible. Review any third-party install scripts before execution.
6. Do not add production Supabase/service-role/payment secrets for planning and UI tasks. Use isolated demo/test values and fixtures. If later required, add secrets in Codex environment secret manager with least privilege, never in prompts, commits, logs, or `NEXT_PUBLIC_*` variables.
7. Validate setup in a first read-only task: `node -v`, `npm -v`, `uv --version`, `npm run typecheck`, `npm test`, `uv run ruff check .`. Run Playwright only when the cloud image has a supported browser; if necessary use `npx playwright install --with-deps chromium` and test against fixtures.
8. Publish/save the cloud environment; start a new task from the accepted branch. Each new task may have a separate workspace; commit/push important changes as PRs.

## Model strategy
Default **GPT-6.1 Sol Medium** where selectable. Do not hardcode speculative model config IDs in repository. If selector has changed, choose an available Sol model with Medium, or another supported model. Escalate reasoning level for narrowly defined security, data migration and race-condition debugging only when required.

## Job execution contract (paste into Codex task)
1. Read `AGENTS.md`, `docs/utbk/README.md`, then only task-specific docs.
2. Summarize existing relevant files and propose smallest diff.
3. Implement **one ticket** from `docs/utbk/TASK_BOARD.md` only.
4. Preserve existing admissions behavior and public routes.
5. Add narrow unit/integration tests and necessary fixture data.
6. Run targeted tests first; run broad checks before PR when practical.
7. Report files changed, tests run/pass/fail, known risks, follow-up issues. Do not claim unrun tests passed.
8. Open a PR for review. Do not auto-merge to main, deploy production, modify billing rules, or manipulate live user data without explicit instruction.

## Token / time budget rules
- Never read the whole repository by default; `rg` paths, `git diff`, `sed` targeted sections.
- Keep `AGENTS.md` short and stable; keep long PRD in `docs/utbk/` on demand.
- Only load `evalio-design` for UI, `evalio-utbk-engine` for question/tryout logic, `evalio-ptn-data` for PTN catalog.
- Delegate by bounded, independent tasks; avoid combining front-end rebrand, database migration, billing and AI in one PR.
- Reuse lockfile/dependencies, existing UI primitives, and existing test framework.
- Avoid placing external skill READMEs into system prompts; use skills' just-in-time lookup.
- Display concise diffs/test summaries instead of full terminal logs, but surface failures.
- Codex Cloud billing/usage is not a guaranteed 'token saving'; measure actual task completion and usage.

## Test/deployment safeguards
Existing `.github/workflows/ci.yml` is the release gate. Tests cover legacy scoring and new UTBK logic; no client-side answer key leaks; do not rely on static GitHub Pages to protect premium data. Deploy new endpoints only after API authorization, RLS, payment entitlements, rate limits and load testing are verified.

## Founder decision gates
G0: docs and cloud setup reviewed; G1: design prototype approved; G2: internal practice alpha; G3: secure tryout + content QA; G4: closed beta with student feedback; G5: payments/launch. No automatic progression just because a task reports 'done'.
