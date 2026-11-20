# EVAL-001 — Evalio UTBK Foundation Audit

**Date:** 2026-11-20  
**Scope:** Repository architecture, reusable components, deployment, security and CI.  
**Status:** Codebase inspection complete; dynamic-runtime security repair remains under review in separate PR #2. This document does **not** certify production readiness.

## 1. Snapshot
- **Repository:** `Suryadharmaa/evalio`; main is an international admissions product.
- **Frontend:** Next.js 16.3.4 + React 19.2.4 + TypeScript 5.9 + Tailwind 4.3 (see `package.json`).
- **Backend:** FastAPI / Python, app entrypoint `api/index.py`, assembly in `api/admission_engine/application/factory.py`.
- **Authentication:** Supabase Auth via `@supabase/ssr` (`lib/auth/server.ts`, `lib/auth/browser.ts`) with backend JWT verification (`api/admission_engine/application/dependencies.py`).
- **Database:** PostgreSQL / SQLAlchemy models in `api/admission_engine/database/models.py`, `api/admission_engine/database/session.py`; Alembic under `migrations/versions/`.
- **Verification:** `npm run lint`, `npm run typecheck`, Vitest, Playwright, Ruff, Mypy, coverage, migration SQL and audits in `.github/workflows/ci.yml`.
- **Deployment:** dynamic Next.js server (Netlify/Vercel-related config) + separately hosted Python API; optional GitHub Pages static export via `scripts/build-pages.mjs` and `.github/workflows/pages.yml`.

## 2. Existing areas we can reuse
| Area | Exact path(s) | UTBK application |
| --- | --- | --- |
| Site and navigation | `components/layout/app-shell.tsx`, `app/layout.tsx` | Add `/utbk` nav without replacing legacy admissions |
| Visual primitives | `components/ui/{button,card,radio-group,dialog,drawer,tabs,progress-bar,source-list,data-freshness-badge}.tsx` | Exam options, card, feedback, PTN sources; check a11y and extension needs |
| Brand | `app/globals.css`, `docs/evalio-DESIGN.md` | Preserve violet/purple calm academic direction |
| Auth | `lib/auth/browser.ts`, `lib/auth/server.ts`, `api/admission_engine/application/dependencies.py` | Owner-scoped attempts, dashboard and purchasing |
| API patterns | `api/admission_engine/application/factory.py`, `api/admission_engine/routers/` | Register isolated `/api/v1/utbk/*` routes, shared error semantics |
| Persistence | `api/admission_engine/database/models.py`, `migrations/env.py` | Add separate UTBK tables via forward-only Alembic revisions |
| Tests | `tests/e2e/`, `tests/python/`, `tests/frontend/` | Add focused tests + regression coverage |
| CI | `.github/workflows/ci.yml` | Keep existing quality gates |

## 3. Proposed module boundaries
- Frontend: `app/utbk/`, `components/utbk/`, `lib/utbk/`.
- API: `api/admission_engine/routers/utbk_*.py` and `api/admission_engine/utbk/` (or `api/utbk/` if agreed after audit). Register with existing application factory.
- DB: `utbk_*` table names, versioned `exam_blueprints` and `attempts`, separate from existing `applicant_profiles` and US colleges.
- Domain scoring: pure deterministic engine; **not** `api/admission_engine/engine/scoring.py` or its V2 implementation. Avoid official scaled UTBK scores and invented passing grades.
- Feature flags and configuration: 2026 baseline is historical; do not claim official 2027 rules until SNPMB confirmation.

## 4. Confirmed risks
1. **CI baseline security regression (HIGH).** As of 2026-11-20, `main` already failed `tests/e2e/home.spec.ts` requiring a CSP nonce; the `proxy.ts` referenced in `docs/SECURITY_AUDIT.md` was absent. See GitHub Actions run `37207087763` (2026-10-04) and later PR #1 run `44662613866`. A **separate** remediation PR #2 attempts to restore per-request server CSP; do not close until tested.
2. **CSP hosting split (HIGH).** Next.js static export does not support Proxy or dynamic response nonces. `scripts/build-pages.mjs` uses HTML SHA-256 CSP meta tags for GitHub Pages; dynamic server needs request nonce. These need independent regression tests and security review.
3. **E2E backend DB missing (MEDIUM).** Playwright starts FastAPI but the CI job does not provide `DATABASE_URL` or a test database; logged API requests emit `RuntimeError: DATABASE_URL is required for persistent operations`. Avoid production secrets in CI; use a dedicated service/fixture or API mocks for tests that do not require persistence. This was already visible on main.
4. **Netlify / GH Pages environment (MEDIUM).** Next config requires `EVALIO_API_ORIGIN` for Netlify and `NEXT_PUBLIC_API_ORIGIN`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` for static export. Actual deployment environment/credentials must be verified in authorized settings; do not assume availability.
5. **Data protection & content rights (HIGH).** No UTBK table/service exists yet; question publication needs license provenance, review controls, answer-key isolation, server-side entitlements, deletion/retention safeguards for student accounts.
6. **No official 2027 rules (PRODUCT).** The exam blueprint must be year-versioned, not hardcoded as 2027.

## 5. Prioritized next PRs
- **PR #2: CI/security remediation** — finish review of server CSP nonce and static export; make Playwright green without disabling the security test. Resolve DB warnings via follow-up testing infrastructure.
- **EVAL-003: UI skeleton** — `/utbk` landing, nav entry, responsive states, existing brand; no DB, payment, migrations, or new dependencies. One small PR.
- **EVAL-005: blueprint schema** — versioned 2026 reference subtests with sources, migrations and tests; no 2027 claims.
- **EVAL-006: question review/content schema** — protected keys, revisioned published items, license and admin role, RLS / authorization.
- **EVAL-008: practice** only after question schema and review workflow prove sound.

## 6. EVAL-001 exit checklist
- [x] Existing architecture and exact reusable files identified.
- [x] Legacy scoring isolation documented.
- [x] Deployment modes and CI risks documented.
- [x] Smallest next PRs proposed and scoped.
- [ ] CI repaired and validated (separate gate).
- [ ] Production credentials/deployment reviewed by repository owner (separate gate).

**Next action:** review this read-only audit, then review security PR #2 and run its full CI. No automatic merge or production deploy.
