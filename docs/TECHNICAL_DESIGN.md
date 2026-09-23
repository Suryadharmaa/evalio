# TECHNICAL_DESIGN.md

# Web Technical Design Specification

**Version:** 2.0.0  
**Deployment:** Vercel  
**Frontend:** Next.js 16.x, React 19.x, TypeScript  
**Backend:** FastAPI/Python 3.12+ deployed as Vercel Python Functions  
**Database:** Supabase PostgreSQL  
**Authentication:** Supabase Auth  
**ORM:** SQLAlchemy 2.x + Alembic  
**Validation:** Pydantic v2 / Zod  
**AI/ML:** Prohibited

---

## 1. Architecture

```text
Browser
  |
  v
Vercel CDN / Next.js
  |
  +----------------------+
  |                      |
  v                      v
React UI             Server rendering
  |
  v
/api/*
  |
  v
FastAPI Python Function
  |
  +----------+-------------+
  |          |             |
  v          v             v
Services   Engine      Repositories
             |             |
             v             v
          Rules       Supabase Postgres
                           |
                           v
                      College data
```

A single Vercel project hosts:

- Next.js at project root;
- Python API under `api/`;
- shared deployment domain.

The deterministic evaluation engine remains framework-independent.

---

## 2. Repository Layout

```text
admission-engine/
├── app/
│   ├── (public)/
│   ├── (auth)/
│   ├── dashboard/
│   ├── essay/
│   ├── colleges/
│   ├── methodology/
│   └── settings/
├── components/
│   ├── ui/
│   ├── forms/
│   ├── charts/
│   └── evaluation/
├── lib/
│   ├── api/
│   ├── auth/
│   ├── schemas/
│   └── utils/
├── public/
├── api/
│   ├── index.py
│   └── admission_engine/
│       ├── application/
│       ├── engine/
│       ├── rules/
│       ├── database/
│       ├── parsers/
│       ├── reports/
│       └── config/
├── scripts/
├── tests/
│   ├── python/
│   ├── frontend/
│   └── e2e/
├── docs/
├── package.json
├── pyproject.toml
├── next.config.ts
├── tsconfig.json
└── .env.example
```

---

## 3. Hard Dependency Boundaries

### UI

May call typed API clients.

Must not:

- implement scoring formulas;
- query production DB directly for private applicant data;
- contain secret keys.

### FastAPI application layer

Owns:

- auth verification;
- request validation;
- transactions;
- orchestration;
- API error mapping.

Must not contain scoring magic numbers.

### Engine

Must:

- be pure/deterministic where possible;
- avoid HTTP/network calls;
- avoid DB sessions;
- avoid framework-specific request objects;
- accept explicit evaluation date when date matters.

### Rules

Must contain versioned thresholds and evidence logic.

### Repositories

Only repository/data-access code may issue persistent DB operations.

---

## 4. Web/API Runtime

Use one FastAPI application exposed through the Vercel `api/` directory.

Recommended endpoint prefix:

```text
/api/v1
```

FastAPI modules:

```text
routers/
services/
engine/
repositories/
schemas/
auth/
errors/
```

Do not create one Vercel Function per scoring rule.

---

## 5. Database Connectivity

Use Supabase PostgreSQL.

Production connection string:

```text
DATABASE_URL
```

Server-only.

For serverless execution:

- avoid process-global transaction state;
- open short-lived sessions per request;
- use a pool strategy compatible with the Supabase connection endpoint chosen;
- never assume a Vercel Function instance persists.

Migrations run from CI/local admin workflow, not during every request.

---

## 6. Authentication Flow

Frontend:

```text
Supabase Auth
→ access token
→ Authorization: Bearer <token>
→ Python API
```

Backend:

1. extract Bearer token;
2. verify token using Supabase-supported verification/JWKS flow;
3. validate issuer/audience/expiration;
4. use verified `sub` as external auth identity;
5. resolve internal user record.

Never trust an unverified client-supplied user ID.

Anonymous endpoints skip auth and must not persist private profile content.

---

## 7. API Contracts

All API responses use a shared envelope.

Success:

```json
{
  "data": {},
  "meta": {
    "request_id": "...",
    "engine_version": "2.0.0"
  }
}
```

Error:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Human-readable message",
    "fields": {}
  },
  "meta": {
    "request_id": "..."
  }
}
```

Detailed endpoint contracts live in `API_SPEC.md`.

---

## 8. Frontend Data Fetching

Use:

- Server Components for public/static college pages where appropriate;
- client components for interactive analyzers/forms;
- typed fetch wrapper for Python API;
- React state only for transient form state;
- no duplicate business formulas in TypeScript.

Do not calculate authoritative admissions scores in the browser.

---

## 9. Upload Flow

V1 direct upload:

```text
Browser
→ multipart request (<4 MB)
→ FastAPI
→ temporary /tmp file or in-memory buffer
→ parser
→ deterministic engine
→ delete temporary content
→ JSON result
```

Supported:

- txt;
- md;
- docx;
- text PDF;
- CSV.

No OCR.

Raw uploads must not be sent to Supabase Storage in V1.

---

## 10. Vercel Constraints

Engineering must assume:

- Function instances are ephemeral;
- local filesystem is temporary;
- persistent state must live in PostgreSQL;
- request/response payloads must remain below platform limits;
- long-running batch imports should run from local/admin scripts or a dedicated job workflow, not an interactive request.

Product direct-upload limit: **4 MB**.

---

## 11. Frontend Stack

Required:

```text
Next.js
React
TypeScript
Tailwind CSS
Zod
```

Recommended:

```text
React Hook Form
Recharts only if charts materially help
```

Avoid excessive UI dependencies.

---

## 12. Python Stack

Required:

```text
FastAPI
Pydantic v2
SQLAlchemy 2.x
Alembic
psycopg
PyMuPDF
python-docx
pytest
ruff
mypy
```

Optional deterministic:

```text
textstat
rapidfuzz
```

Prohibited:

```text
OpenAI
Anthropic
Gemini
Ollama
Transformers
PyTorch
TensorFlow
sentence-transformers
LangChain
LlamaIndex
vector databases
```

---

## 13. Configuration

Frontend public:

```text
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
NEXT_PUBLIC_APP_URL
```

Server-only:

```text
DATABASE_URL
SUPABASE_URL
SUPABASE_SECRET_KEY
SUPABASE_JWKS_URL
ADMIN_USER_IDS
IP_HASH_SALT
APP_ENV
LOG_LEVEL
```

Never prefix secrets with `NEXT_PUBLIC_`.

---

## 14. Error Taxonomy

```text
INVALID_INPUT
UNAUTHORIZED
FORBIDDEN
NOT_FOUND
CONFLICT
UNSUPPORTED_FILE
FILE_TOO_LARGE
NO_EXTRACTABLE_TEXT
REQUIREMENT_INCOMPLETE
STALE_COLLEGE_DATA
RATE_LIMITED
DATABASE_ERROR
INTERNAL_ERROR
```

HTTP mapping:

```text
400 invalid input
401 unauthenticated
403 forbidden
404 missing resource
409 conflict
413 payload too large
422 structured validation failure
429 rate limited
500 internal error
```

---

## 15. Logging

Structured JSON logs.

Allowed:

- request ID;
- route;
- status;
- duration;
- internal user ID or hashed anonymous ID;
- engine/rubric version;
- error code.

Forbidden:

- raw essay;
- raw LOR;
- transcript text;
- access tokens;
- passwords;
- database credentials;
- raw upload body;
- detailed family-finance values.

---

## 16. Determinism

Authoritative score must be generated in Python engine.

Forbidden nondeterminism:

- random scoring;
- hidden current-date dependency;
- unordered rule application;
- remote HTTP calls during scoring;
- client-side score mutation.

Every evaluation stores:

```text
engine_version
rubric_version
input_hash
evaluation_date
```

---

## 17. Source Data Updates

Workflow:

```text
Official source/data file
→ local/admin importer
→ staging
→ validation
→ diff
→ manual approval
→ production
```

Never let a normal public web request overwrite verified college reference data.

---

## 18. Performance Targets

Typical:

```text
public college page          < 2.5s LCP target
simple API response          < 1s
650-word essay analysis      < 2.5s typical
activity evaluation          < 1s
college evaluation           < 2s
report data generation       < 5s
```

Do not sacrifice correctness for these targets.

---

## 19. Caching

Safe to cache:

- public college records;
- methodology;
- rule metadata;
- static dictionaries.

Never shared-cache:

- user profiles;
- saved essays;
- private reports.

Use appropriate `Cache-Control` headers.

---

## 20. Deployment

Vercel project connected to Git repository.

Environments:

```text
local
preview
production
```

Each environment uses separate database configuration where feasible.

Pull requests may create preview deployments, but previews must not point to production user data unless intentionally configured.

---

## 21. Definition of Technical Done

- Next.js and Python API deploy together;
- PostgreSQL persistence works;
- Supabase Auth tokens are verified server-side;
- anonymous analyzers work without persistence;
- engine contains no web-framework logic;
- web layer contains no scoring formulas;
- direct uploads are <4 MB and deleted after processing;
- migrations are reproducible;
- all critical tests pass;
- no AI dependency exists.
