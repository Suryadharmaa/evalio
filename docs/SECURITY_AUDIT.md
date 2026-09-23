# Evalio Security Audit

Audit date: 2026-09-12. Scope: TypeScript/React/Next.js frontend and Python/FastAPI API, scripts, dependencies, and deployment configuration.

## Resolved findings

### SEC-001 — Medium — Permissive browser script policy

- Location: `proxy.ts`, formerly `next.config.ts` response headers.
- Evidence: the former static policy required inline script permission; responses now receive a per-request nonce and `strict-dynamic`, with `unsafe-eval` limited to development.
- Impact: a permissive CSP weakens defense in depth against injected scripts.
- Fix: nonce-based CSP on request and response, dynamic rendering via `connection()`, frame denial, content-type, referrer, permissions, and production HSTS headers.
- Mitigation/false positive: React escaping already reduced exploitability; CSP is defense in depth. Runtime header behavior still requires deployed-environment verification.

### SEC-002 — Medium — Unbounded document expansion

- Location: `api/admission_engine/parsers/documents.py` and upload route.
- Evidence: compressed documents could consume excessive CPU/memory during extraction.
- Impact: resource-exhaustion denial of service.
- Fix: 4 MB direct upload limit, archive/magic validation, PDF page cap, DOCX member/expanded/XML caps, and 100,000 extracted-character cap.
- Mitigation/false positive: serverless duration/memory limits reduce blast radius but are not a substitute for input bounds.

### SEC-003 — Medium — Saved-report schema allowed arbitrary sections

- Location: `api/admission_engine/schemas/reports.py`, `routers/reports.py`.
- Evidence: caller-defined nested report content could bypass the intended metrics-only shape.
- Impact: unintended persistent storage/redisplay of sensitive raw applicant text.
- Fix: saved reports now accept only `APPLICATION_READINESS`, bounded profile metadata, and at most 20 typed evaluation summaries; raw-text key defense remains.
- Mitigation/false positive: reports are owner-scoped, but authorization alone does not enforce privacy-by-default.

### SEC-004 — Medium — Public rate-limit identity bypass

- Location: `api/admission_engine/application/factory.py`.
- Evidence: arbitrary bearer values could previously create distinct public-route limiter subjects.
- Impact: public analysis quotas could be bypassed for resource exhaustion.
- Fix: public routes always use client address; authenticated limits use the verified JWT subject rather than raw/forged bearer text. Production counters use atomic PostgreSQL upsert and remove expired buckets through an indexed expiry column.
- Mitigation/false positive: upstream proxy address preservation must be verified on Vercel.

### SEC-005 — Low — Missing host/origin allow-lists

- Location: `api/admission_engine/application/factory.py`, `config/settings.py`.
- Evidence: host headers were not constrained and the CORS origin setting did not have a documented production environment variable.
- Impact: host-header misuse in future absolute URL generation or proxy behavior.
- Fix: `TrustedHostMiddleware`; explicit `ALLOWED_HOSTS` and `ALLOWED_ORIGINS`; production rejects missing, wildcard, credential-bearing, path-bearing, or non-HTTPS origin configuration.
- Mitigation/false positive: current endpoints do not construct security-sensitive absolute URLs from Host.

### SEC-006 — Low — Import staging path and malformed-domain handling

- Location: `scripts/college_import.py`.
- Evidence: unconstrained run identifiers and malformed numeric/enum fields could address unintended paths or crash validation.
- Impact: local/admin pipeline file access outside staging and unreliable validation.
- Fix: hex run IDs, file/row caps, slug/country/enum checks, and explicit malformed numeric reporting.
- Mitigation/false positive: script is admin/local, not a public HTTP endpoint; reduced exposure does not remove the trust-boundary issue.

### SEC-007 — Low — Upload form cross-field error could become 500

- Location: `api/admission_engine/routers/evaluations.py`.
- Evidence: malformed word bounds created a model-level validation exception after form parsing.
- Impact: incorrect error handling and avoidable exception load.
- Fix: constrained form parameters and explicit `min_words <= word_limit` domain validation returning a controlled client error.
- Mitigation/false positive: no confidentiality/integrity impact was found.

### SEC-008 — Low — External URLs could contain credentials

- Location: `lib/utils/safe-url.ts`, `scripts/college_import.py`.
- Evidence: HTTP(S) user-info URLs passed the protocol allow-list.
- Impact: confusing links and possible credential disclosure in rendered targets/logs.
- Fix: frontend rendering and the college import pipeline reject URLs with username or password in addition to rejecting non-HTTP(S) protocols.
- Mitigation/false positive: links already used `noopener noreferrer`; this further constrains accepted data.

### SEC-009 — Low — API discovery endpoints exposed in production

- Location: `api/admission_engine/application/factory.py`.
- Evidence: framework OpenAPI/Swagger/ReDoc endpoints were enabled by default.
- Impact: unnecessary production attack-surface enumeration.
- Fix: OpenAPI, Swagger, and ReDoc endpoints disabled.
- Mitigation/false positive: endpoint secrecy is not an authorization control; all protected routes still enforce identity and ownership.

### SEC-010 — Medium — Incomplete metrics persistence and account export

- Location: `api/admission_engine/database/models.py`, `routers/profile_data.py`, `routers/account.py`, migration `20260913_0003`.
- Evidence: metrics-only saved essays retained scores/components but not the documented essay-metric record; exports omitted essay metrics, evaluation components, and triggered-rule evidence.
- Impact: privacy controls could provide an incomplete user-data export and saved analysis history could lose explainability data.
- Fix: added cascade-owned `essay_metrics`, persisted deterministic metrics, exposed saved detail safely, and included all three child datasets in account export.
- Mitigation/false positive: raw essay text already remained opt-in; this finding concerns data completeness and portability, not cross-user disclosure.

## Residual deployment checks

- Verify nonce CSP, forwarded client address, HSTS, CORS, and trusted-host behavior on preview and production.
- Verify Supabase redirect allow-lists, separate preview/production projects, JWT issuer/audience, secrets, migrations, backups, and database grants/RLS posture.
- Confirm platform request-body and function resource limits remain at or below documented caps.
- Run authenticated cross-user, export, deletion, admin, and rate-limit smoke against the deployed database.

No unresolved code-level P0/P1 finding was identified. Production release remains blocked on the external checks above.

## Verification evidence

- `ruff --select S`: clean.
- Ownership, token, admin, upload, report, import, header, and validation tests included in 92 passing Python tests.
- Nonce CSP and absence of `unsafe-inline` verified by Playwright.
- npm audit reported 0 vulnerabilities; Python audit reported no known vulnerabilities.
- Secret/prohibited-dependency/static unsafe-pattern scans found no committed credential or AI/LLM/ML dependency.
