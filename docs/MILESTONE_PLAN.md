# MILESTONE_PLAN.md

# Web Implementation Roadmap for Codex

**Version:** 2.0.0

---

## Working Rule

Codex must implement one milestone at a time.

For every milestone:

1. read `AGENTS.md` if present;
2. read all relevant docs;
3. inspect existing code;
4. implement only scope;
5. add/update tests;
6. run required checks;
7. inspect diff;
8. summarize changes;
9. stop.

---

## M0 — Repository Foundation

Create unified Next.js + Python Vercel project.

Required:

- Next.js/TypeScript;
- Python/FastAPI;
- pytest/ruff/mypy;
- Vitest/Playwright;
- env example;
- docs;
- Git ignore;
- no AI dependencies.

Acceptance:

```text
Next dev app runs
Python API health endpoint runs
tests execute
production build succeeds
```

---

## M1 — Web Design Foundation

Build:

- application shell;
- navigation;
- typography;
- spacing/tokens;
- form primitives;
- score card;
- alert/status components;
- loading/error/empty states;
- responsive layout.

No admissions logic.

---

## M2 — Python Domain + Rule Framework

Implement:

- enums;
- Pydantic models;
- RuleResult;
- rule registry;
- version constants;
- deterministic rule ordering.

---

## M3 — PostgreSQL + Auth Foundation

Implement:

- Supabase Auth frontend setup;
- token verification backend;
- SQLAlchemy/Postgres;
- Alembic;
- user/profile base tables;
- ownership middleware/helper.

Acceptance includes cross-user access denial tests.

---

## M4 — Applicant Profile

Build API + UI:

- profile setup;
- curriculum;
- grading scale;
- intended major;
- school context.

---

## M5 — Academic Engine

Implement exact `SCORING_SPEC.md` academic behavior.

Expose:

```text
POST /api/v1/evaluations/academic
```

Build dashboard academic section.

---

## M6 — Activity Engine

Implement:

- individual scoring;
- portfolio;
- description analysis;
- activity UI;
- API endpoints.

---

## M7 — Honors Engine

Implement honor scoring + UI.

---

## M8 — Essay Metrics

Implement deterministic text metrics and parsers independent of web.

No score UI yet beyond raw metrics test harness.

---

## M9 — Essay Scoring

Implement all essay scoring/rules.

Expose anonymous and authenticated analysis endpoint.

Build `/essay` results UI.

---

## M10 — Essay Compare & History

Authenticated:

- saved drafts opt-in;
- compare two evaluations;
- delta UI.

Anonymous compare may operate only within current browser session without server persistence.

---

## M11 — LOR Signal Engine

Implement text signals + protected authenticated UI.

Raw text storage remains opt-in.

---

## M12 — File Parsers

Implement:

- TXT;
- MD;
- DOCX;
- text PDF;
- CSV.

Direct upload max 4 MB.

No OCR.

---

## M13 — College Database

Implement:

- college reference tables;
- source provenance;
- requirements;
- aid;
- CDS;
- admissions ranges.

---

## M14 — Import/Staging Pipeline

Local/admin scripts:

```text
import
validate
diff
approve
promote
```

No automatic public scraping.

---

## M15 — College Explorer

Build:

```text
/colleges
/colleges/[slug]
```

Features:

- search;
- filters;
- verified data;
- source/freshness display.

---

## M16 — College Evaluation

Implement:

- academic alignment;
- requirements fit;
- selectivity risk;
- data confidence;
- planning category;
- why-result detail.

---

## M17 — Financial Fit

Implement budget/aid policy evaluator.

No precise admission probability penalty.

---

## M18 — Application Audit

Implement target-college checklist and priority issues.

Separate completeness from quality.

---

## M19 — Dashboard Integration

Build complete dashboard:

- PSI;
- components;
- targets;
- readiness;
- issues;
- navigation to fixes.

---

## M20 — Reports

Implement structured report JSON and printable web report.

PDF export is optional after printable page is stable.

---

## M21 — Methodology & Explainability

Build public:

```text
/methodology
```

and component-specific methodology pages.

Every result view exposes `Why?`.

---

## M22 — Privacy Controls

Implement:

- export my data;
- delete my data;
- saved-content controls;
- privacy page.

---

## M23 — Security Hardening

Implement/test full `SECURITY.md`:

- rate limits;
- CSP/security headers;
- input caps;
- XSS;
- ownership;
- admin authorization;
- log redaction;
- upload safeguards.

---

## M24 — Calibration & Golden Fixtures

Build/review synthetic fixtures:

```text
30+ essays
20+ academic profiles
20+ activity portfolios
10+ LORs
20+ college scenarios
```

Finalize rubric version for release.

---

## M25 — Vercel/Supabase Deployment

Configure:

- preview environment;
- production environment;
- migrations;
- Supabase auth redirects;
- production env vars;
- health checks.

Do not connect preview to production user data unless intentionally approved.

---

## M26 — Production QA

Manual smoke:

```text
anonymous essay
signup/login
profile
academics
activities
honors
college search
college evaluation
audit
report
export
delete
mobile
```

Release only if all P0/P1 issues resolved.

---

## Recommended Codex Prompt

```text
Implement Milestone M<n> from docs/MILESTONE_PLAN.md.

Before coding, read:
- PRD.md
- TECHNICAL_DESIGN.md
- API_SPEC.md
- UI_UX_SPEC.md
- DATA_SPEC.md
- SCORING_SPEC.md
- RULEBOOK.md
- TEST_PLAN.md
- SECURITY.md

The specifications are authoritative.

Hard constraints:
- no LLM
- no AI API
- no local AI
- no ML
- no embeddings/vector DB
- do not implement future milestones

After implementation:
1. run relevant Python tests
2. run ruff/mypy
3. run frontend tests/typecheck where relevant
4. run production build if web code changed
5. inspect git diff
6. summarize files changed and unresolved issues
7. stop
```
