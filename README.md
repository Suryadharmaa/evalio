# Evalio

Deterministic, explainable college admissions evaluation engine.

## Requirements

- Node.js 20.9+
- npm 10+
- Python 3.12+
- uv

## Local development

```bash
npm install
uv sync
npm run dev
uv run uvicorn api.index:app --reload --port 8000
```

The Next.js application runs on `http://localhost:3000`. The FastAPI health endpoint
is available at `http://localhost:8000/api/v1/health` during standalone local API
development.

For GitHub Pages, `.github/workflows/pages.yml` builds and publishes a static
frontend. Supabase handles login/data and FastAPI runs on a separate Python host.
Follow [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md#github-pages--supabase--fastapi).

Enable **Settings → Pages → Source: GitHub Actions**. Then set these repository
**Settings → Secrets and variables → Actions → Variables**:

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_ORIGIN` | Your live FastAPI HTTPS origin, e.g. `https://your-api.onrender.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Your Supabase publishable key |

These values are public browser configuration. Backend secrets (`DATABASE_URL`,
`GEMINI_API_KEY`, Supabase secret key) belong only on the Python host. The workflow
detects `NEXT_PUBLIC_BASE_PATH` for `/evalio` or a custom domain automatically.

To check the Pages build locally in PowerShell (Supabase values in `.env.local`):

```powershell
$env:NEXT_PUBLIC_API_ORIGIN="https://your-api.onrender.com"
$env:NEXT_PUBLIC_BASE_PATH="/evalio"
npm run build:pages
npm run preview:pages
```

The site is generated in `out/`; preview opens at `http://127.0.0.1:4173/evalio/`
and uses the configured base path automatically. `npm run test:pages` checks
the exported frontend using synthetic API responses. `npm run start` runs a Next.js server
and does not preview a static export. Mutable detail links use `/view/?slug=...`
or `/view/?id=...`; new database records work without rebuilding the site.

### Scoring engine rollout

V1 remains the default while the isolated V2 domains are validated:

```text
SCORING_ENGINE_VERSION=v1
```

Set `SCORING_ENGINE_VERSION=v2` only in a V2 development/test environment. The
switch does not rewrite or re-score saved V1 evaluations. V2 is not yet wired to
production evaluation routes.

## College seed data

The initial US reference dataset contains 200 colleges:

```text
data/seed/evalio_top200_us_colleges_enriched.csv
```

The importer writes college identity, 2026-27 admissions, financial-aid data, and
source provenance into PostgreSQL/Supabase. It validates the entire file before
opening a write transaction, and repeated imports update existing records by slug
instead of creating duplicate colleges.

### 1. Configure the database

Set `DATABASE_URL` in `.env.local` to the PostgreSQL connection string for the
intended Supabase project. Keep database credentials private and never commit
`.env.local`.

### 2. Apply the database migration

Run the latest Alembic migration before importing. It adds the college city and
application-platform fields required by this dataset:

```bash
uv run alembic upgrade head
```

You can confirm the migration head without changing the database:

```bash
uv run alembic heads
```

The expected head is `20260923_0011`.

### 3. Validate with a dry run

Always run the dry run first:

```bash
uv run python scripts/import_colleges.py data/seed/evalio_top200_us_colleges_enriched.csv --dry-run
```

Dry-run validates all rows and prints the planned college, admissions,
financial-aid, and source upserts. It does not connect to or modify the database.
The supplied dataset should report 200 rows read, 200 valid rows, and zero rejected
rows. Blank numeric values remain `NULL`; no missing values are fabricated.

### 4. Perform the real import

After reviewing the dry-run report and confirming that `DATABASE_URL` points to the
correct database, explicitly authorize the write:

```bash
uv run python scripts/import_colleges.py data/seed/evalio_top200_us_colleges_enriched.csv --confirm IMPORT
```

The command prints inserted and updated counts for every destination table. The
write uses one transaction: a database error rolls back the complete import.

### 5. Verify through the API

Start the API and frontend in separate terminals:

```bash
uv run uvicorn api.index:app --reload --port 8000
```

```bash
npm run dev
```

Open `http://localhost:3000/colleges`, or query the API directly:

```text
GET http://localhost:8000/api/v1/colleges?country=US&page=1&page_size=20
GET http://localhost:8000/api/v1/colleges?q=Princeton&country=US
GET http://localhost:8000/api/v1/colleges?application_platform=COMMON_APP
GET http://localhost:8000/api/v1/colleges/princeton-university
```

Available list filters are `q`, `country`, `state`, `test_policy`, `need_policy`,
`application_platform`, `institution_type`, `selectivity_band`, `page`, and
`page_size`. Country defaults to `US`; an omitted state searches all states.

### Import normalized Batch 1 with Batch 2A/2B enrichment

The normalized research package lives in `data/data_v2/seed`. The importer loads
Batch 1 first, then applies `batch_2a` and `batch_2b` field-level enrichment for
the first 100 researched institutions. `UNKNOWN`, `PENDING`, nuanced aid policies,
and blank values are preserved.

Validate every source row without opening a database connection:

```powershell
uv run python scripts/import_college_batch.py data/data_v2/seed --dry-run
```

After applying migrations and confirming `DATABASE_URL` points to a non-production
database, import into staging explicitly:

```powershell
uv run alembic upgrade head
$env:APP_ENV = "staging"
uv run python scripts/import_college_batch.py data/data_v2/seed --environment staging
```

The importer refuses all writes when `APP_ENV=production`. Unverified fees remain
blank and are reported as warnings, including Batch 2A's unresolved Purdue conflict.

### Apply the September 2026 college-data refresh

`data/Update_Data` is a field-level refresh on top of the normalized Batch 1/2
dataset. It refreshes policies for 200 colleges, detailed admissions and costs for
12 colleges, and source provenance. The audit workbook, gap report, and change
report are review artifacts and are never written to the database.

Run the normalized Batch 1/2 import first. Then apply migration `20260920_0010`,
which adds international admissions counts, CSS Profile status, and books/personal
cost fields:

```powershell
uv run alembic upgrade head
uv run python scripts/import_college_refresh.py data/Update_Data --dry-run
```

The dry run must report 200 policy rows, 12 admissions rows, 12 financial-aid
rows, and 230 deduplicated source records. It does not open a database connection.
The refresh intentionally preserves canonical Batch 1 identities instead of four
incorrect legacy identities still present in the wide input file.

After checking the report and confirming `DATABASE_URL`, write only to local or
staging explicitly:

```powershell
$env:APP_ENV = "staging"
uv run python scripts/import_college_refresh.py data/Update_Data --environment staging
```

The importer refuses `APP_ENV=production`, requires all 200 normalized colleges
to exist first, runs in one transaction, and is idempotent for source provenance.

### Import troubleshooting

- `DATABASE_URL is required`: add a valid PostgreSQL URL to `.env.local`.
- Missing-column or invalid-value errors: fix the CSV and rerun dry-run. The importer
  never silently skips malformed rows.
- Missing college columns at runtime: run `uv run alembic upgrade head` against the
  same database used by the importer and API.
- API connection errors: confirm the FastAPI service is running on port 8000 and the
  Supabase database accepts the configured connection.

## Hybrid Essay Review

The Essay Evaluator at `/tools/essay-evaluator` now combines local writing
signals with one structured semantic review. The existing deterministic essay
endpoint and saved historical evaluations retain their previous rubric.

Choose one provider in `.env.local` for the FastAPI process. Gemini is now the
default:

```dotenv
ESSAY_AI_PROVIDER=gemini
GEMINI_API_KEY=your-google-gemini-server-side-key
ESSAY_AI_MODEL=gemini-3.5-flash-lite
```

For Gemini only, HTTP 429 triggers this ordered fallback using the same Google
API key: `gemini-3.5-flash-lite` → `gemini-3.1-flash-lite` →
`gemma-4-26b-a4b-it` → `gemma-4-31b-it`. Each limited model is attempted once,
and other errors stop the chain. Successful fallback reviews are cached under
the actual model; Deep Review can reuse that analysis. If every model is limited,
only local writing signals are returned. Daily quotas vary by project/tier and
are not hardcoded as guarantees.

To use Groq instead:

```dotenv
GROQ_API_KEY=your-server-side-key
ESSAY_AI_PROVIDER=groq
```

To use Routeway instead:

```dotenv
ESSAY_AI_PROVIDER=routeway
ROUTEWAY_API_KEY=your-routeway-server-side-key
ESSAY_AI_MODEL=gemma-4-26b-a4b-it-chimerax:free
```

`ESSAY_AI_MODEL` is optional: Gemini defaults to `gemini-3.5-flash-lite`, Groq defaults to `openai/gpt-oss-20b`, and
Routeway defaults to `gemma-4-26b-a4b-it-chimerax:free`. Never expose either
key as a `NEXT_PUBLIC_` variable. On a separately hosted FastAPI backend, set
these variables on that backend, not Netlify. Apply migrations, then
start the API and frontend in separate terminals:

```powershell
uv run alembic upgrade head
uv run uvicorn api.index:app --reload --port 8000
```

```powershell
npm run dev
```

The new endpoints are `POST /api/v1/essay-review` with `{ "essay": "..." }`
and the user-triggered `POST /api/v1/essay-review/deep` with the returned
`analysis_id` and the same essay. The standard review accepts 50–5,000 words.
The database cache stores the essay hash, versions, local metrics, and structured
result; it does not store raw essay text. Without an API key or if AI fails,
the response still contains writing signals and a retry option. The model
uses [Groq Structured Outputs](https://console.groq.com/docs/structured-outputs)
with a strict JSON schema for Groq. Gemini uses Google's OpenAI-compatible endpoint
with structured JSON output. Routeway receives a JSON-only prompt and
its result must pass the same server-side rubric validation before a score is
shown. If the selected Routeway free model is unavailable or rate-limited, the
tool retains local writing signals without inventing a score.

If the provider returns only writing signals, test the configured provider
with a synthetic essay (one API call; no user essay or key is printed):

```powershell


```


A Routeway HTTP 429 means the selected model/key has reached a provider limit,
even if a separate synthetic diagnostic call succeeds later. Evalio does not
immediately retry 429 responses; it preserves local writing signals and honors
the provider's numeric `Retry-After` header (or a 60-second UI pause when absent).
Check the free-model quota/reset in Routeway. For production reliability, choose
an available plan/model or switch back to Groq explicitly; Evalio never sends an
essay to a second provider as a silent fallback.

## Application Evaluator

1. Sign in and create a saved profile, including academic history and any available
   activities, honors, testing, essay, or recommendation evaluations.
2. Open `http://localhost:3000/tools/application-evaluator` or select
   **Evaluate My Profile** from a college detail page.
3. Select the saved profile, search for a target college, and choose an explicit
   evaluation date.
4. Run the evaluation and inspect each dimension, `N/A` values, college data cycles,
   source freshness, reasons, and triggered rule IDs separately.

The planning category is not an admission probability, guarantee, or safety label.
The authenticated API route is:

```text
POST /api/v1/profiles/{profile_id}/colleges/{college_id}/evaluate
```

---

## LOR Builder

1. Open `http://localhost:3000/tools/lor-builder`.
2. Enter the recommender relationship, observed qualities, and at least one concrete
   example. Optional evidence should only be added when directly supportable.
3. Select the intended endorsement strength and build the framework.
4. Edit each section directly or copy the full framework for recommender review.

The tool does not save input, invent facts, or produce final recommender-owned prose.
Its public API route is `POST /api/v1/lor/build`.

---

## Quality checks

```bash
npm run lint
npm run typecheck
npm test
npm run test:e2e
npm run build
uv run ruff check .
uv run ruff check api scripts --select S
uv run mypy
uv run pytest
uv run coverage run --source=api/admission_engine/engine -m pytest tests/python
uv run coverage report --fail-under=90
npm audit
uvx pip-audit
```

Product behavior and milestones are defined in [`docs/`](docs/). Deployment and production smoke steps are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) and [`docs/QA_RUNBOOK.md`](docs/QA_RUNBOOK.md).
### Import licensed college media

After applying migrations, validate the curated media file without changing the database:

```powershell
uv run python scripts/import_college_media.py data/seed/college_media.csv --dry-run
```

To import or update the verified media records explicitly:

```powershell
uv run python scripts/import_college_media.py data/seed/college_media.csv --confirm IMPORT
```

Only allowlisted HTTPS image hosts and compatible licenses are accepted. Each record retains its source URL, attribution, alt text, dimensions, and verification date.

### Import college logos — Batches 1–4

The curated manifest is stored in `data/research/logo-batch1`. Validate it first;
this performs no download and no database write:

```powershell
uv run python scripts/import_college_logos.py data/research/logo-batch1/college_logos_batch1.csv
uv run python scripts/import_college_logos.py data/research/logo-batch2/college_logos_batch2.csv
uv run python scripts/import_college_logos.py data/research/logo-batch3/college_logos_batch3.csv
uv run python scripts/import_college_logos.py data/research/logo-batch4/college_logos_batch4.csv
```

Download and inspect the 24 approved local assets, then generate the media import CSV:

```powershell
uv run python scripts/import_college_logos.py data/research/logo-batch1/college_logos_batch1.csv --download --write-media-csv
uv run python scripts/import_college_logos.py data/research/logo-batch2/college_logos_batch2.csv --download --write-media-csv
uv run python scripts/import_college_logos.py data/research/logo-batch3/college_logos_batch3.csv --download --write-media-csv
uv run python scripts/import_college_logos.py data/research/logo-batch4/college_logos_batch4.csv --download --write-media-csv
```

Entries marked `PENDING_OFFICIAL_DOWNLOAD`, including University of Notre Dame,
remain on the Evalio initials fallback. Do not replace them with athletics or
unverified marks. Review all `MEDIUM` assets before production.

After reviewing the downloaded files, apply the latest migration and import into a
non-production database with the existing guarded importer:

```powershell
uv run alembic upgrade head
uv run python scripts/import_college_media.py data/research/logo-batch1/college_media_logo_import.csv --dry-run
uv run python scripts/import_college_media.py data/research/logo-batch1/college_media_logo_import.csv --confirm IMPORT
```

Repeat the two guarded media-import commands for `logo-batch2`, `logo-batch3`, and
`logo-batch4`.

The last command writes to the configured `DATABASE_URL`; verify the target first.
The importer is idempotent by college and image URL, and primary media is isolated
per media type so a logo never replaces a primary campus photograph.
