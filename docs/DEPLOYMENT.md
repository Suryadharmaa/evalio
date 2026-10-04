# Deployment

## Supabase

1. Create separate preview and production projects.
2. Set `DATABASE_URL` to the pooler connection using the `postgresql+psycopg://` scheme.
3. Run `uv run alembic upgrade head` from a trusted deployment job.
4. Configure the Auth redirect allow-list for the matching deployment domains.
5. Never expose the Supabase secret key through `NEXT_PUBLIC_*` variables.
6. Set `ALLOWED_HOSTS` to the exact comma-separated API hostnames (no scheme or path).
7. Set `ALLOWED_ORIGINS` to the exact comma-separated HTTPS application origins used by each environment.

## Vercel

Import this repository as a Next.js project and configure the variables listed in `.env.example`. Use different secrets and databases for preview and production. Vercel discovers the FastAPI `app` exported by `api/index.py` and routes `/api/*` to it while preserving the original path.

Before promotion, run the CI suite and `uv run python scripts/production_smoke.py --base-url <preview-url>`. The smoke test requires both liveness and `/api/v1/health/ready` to confirm the deployed database is at the expected Alembic revision. After deployment, repeat it against production and follow `docs/QA_RUNBOOK.md`.

## GitHub Pages + Supabase + FastAPI

This is the current launch architecture. GitHub Actions exports the frontend;
GitHub Pages serves static files. The browser signs in with Supabase Auth and
calls FastAPI directly with bearer tokens. FastAPI enforces authentication,
record ownership and admin permissions. GitHub Actions does not host the API.

### Deploy FastAPI

The repository includes `render.yaml` for a Render Blueprint with one free Python
web service, Python 3.12, the correct commands, a generated IP hash salt, and
`ALLOWED_HOSTS` derived from the assigned Render hostname. Choose **New → Blueprint**
and this repository to use it. Supply database/Supabase/Gemini settings privately
when Render prompts. Auto-deploy is disabled initially; trigger later updates
manually after checks. No database migration or CSV import runs automatically.

On a Python host such as Render, connect this repository as a **Web Service**
using the repository root and these commands:

```text
Build: pip install uv && uv sync --frozen --no-dev
Start: uv run --no-sync uvicorn api.index:app --host 0.0.0.0 --port $PORT
Health check: /api/v1/health
```

The assigned public HTTPS URL is `NEXT_PUBLIC_API_ORIGIN`. Use the origin without
a path or trailing slash. Set the following on the Python host:

```dotenv
APP_ENV=production
DATABASE_URL=postgresql+psycopg://user:password@your-pooler:6543/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWKS_URL=https://your-project.supabase.co/auth/v1/.well-known/jwks.json
IP_HASH_SALT=your-long-random-secret
ALLOWED_HOSTS=your-api.onrender.com
ALLOWED_ORIGINS=https://suryadharmaa.github.io
ESSAY_AI_PROVIDER=gemini
GEMINI_API_KEY=your-server-side-key
ESSAY_AI_MODEL=gemini-3.5-flash-lite
```

Replace `ALLOWED_HOSTS` with the actual API hostname. CORS origins do not contain
`/evalio`; add your custom HTTPS frontend origin if applicable. `.env.local` is
not uploaded automatically. Apply migrations in a trusted job before release:
`uv run alembic upgrade head`. The Pages workflow does not migrate or import data.
Confirm both `/api/v1/health` and `/api/v1/health/ready` return HTTP 200.

### Supabase Auth

For `Suryadharmaa/evalio`, the default frontend URL is
`https://suryadharmaa.github.io/evalio/`. Set that **Site URL** in Supabase Auth URL
Configuration and allow redirects under `https://suryadharmaa.github.io/evalio/**`.
Keep localhost entries for development; add your custom domain if applicable.
Password login, confirmations and magic links use browser-managed sessions.
Keep existing database RLS enabled and backend credentials only on the API host.

### GitHub settings

Choose **Settings → Pages → Build and deployment → Source: GitHub Actions**.
Under **Settings → Secrets and variables → Actions → Variables**, add:

- `NEXT_PUBLIC_API_ORIGIN`: the live FastAPI HTTPS origin.
- `NEXT_PUBLIC_SUPABASE_URL`: your Supabase project URL.
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`: the publishable key.

Push to `main` or run **Actions → Deploy GitHub Pages → Run workflow**. The workflow
detects the Pages base path, builds via `npm run build:pages`, uploads `out/` and
publishes via the `github-pages` environment. Rebuild after changing variables.

### Verify deployment

Open the home page, colleges, a college detail and a public tool; refresh their
URLs. Sign in, open Dashboard, save a profile and sign out. Test confirmation and
magic links returning to `/evalio/`. Browser API requests must reach the API host.
Run the backend smoke script against the API origin (not the Pages URL):

```powershell
uv run python scripts/production_smoke.py --base-url https://your-api.onrender.com
```

The export includes `.nojekyll` and per-page CSP hashes for inline Next.js scripts.
GitHub Pages does not apply Next.js response headers or nonce middleware; a CSP
meta policy is inserted by the build. Private database data is fetched after
login and is not embedded in the static site. Mutable detail routes now use
`/colleges/view/?slug=...`, `/essays/view/?id=...`, `/reports/view/?id=...`, and
`/application/view/?id=...`. Replace old ID-based bookmarks with these links.

## Netlify frontend + separately hosted FastAPI

The default essay provider is now Gemini. On the FastAPI host set
`ESSAY_AI_PROVIDER=gemini`, `GEMINI_API_KEY`, and
`ESSAY_AI_MODEL=gemini-3.5-flash-lite`. Keep the key server-side; do not put it
in Netlify's `NEXT_PUBLIC_*` variables. Groq and Routeway remain alternatives.

Netlify hosts the Next.js frontend, but does not deploy the Python `api/index.py` FastAPI app as a Netlify Function. Host the existing FastAPI ASGI app on a Python-capable service at a stable HTTPS origin. The frontend proxies `/api/v1/*` to that origin through the Next.js rewrite in `next.config.ts`; users continue to call the same-origin path. No production database import or deployment is performed by this repository configuration.

1. Deploy the FastAPI app using `api.index:app`, with a production Python environment and a Supabase production database. Apply `uv run alembic upgrade head` from a trusted job before accepting traffic. Check `https://<api-host>/api/v1/health` and `/api/v1/health/ready` (both must return HTTP 200).
2. Set backend `APP_ENV=production`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `IP_HASH_SALT`, `ALLOWED_HOSTS=<api-host>`, and `ALLOWED_ORIGINS=https://<site>.netlify.app` (plus your final custom HTTPS origin, if used). For essay AI, set `ESSAY_AI_PROVIDER=groq` with `GROQ_API_KEY`, or `ESSAY_AI_PROVIDER=routeway` with `ROUTEWAY_API_KEY`; `ESSAY_AI_MODEL` may override the provider default. Set provider keys only on the backend. Never place backend secrets in Netlify `NEXT_PUBLIC_*` variables.
3. In Netlify, connect the repository as a Next.js project. `netlify.toml` sets build command `npm run build` and publish directory `.next`. Set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, and `EVALIO_API_ORIGIN=https://<api-host>` in Netlify environment variables. The latter must be an HTTPS origin without a trailing slash or path; a Netlify build fails if it is absent.
4. Add the Netlify and final custom domain redirect URLs to Supabase Auth. For each deploy context, use matching frontend/backend/database settings; never point a preview at production by accident.
5. Before release, run `uv run python scripts/production_smoke.py --base-url https://<site>.netlify.app`, sign in, open Dashboard and College Explorer, run a tool, and check `/api/v1/health/ready` through the Netlify URL. Repeat on the custom domain after DNS/TLS setup.

Do not launch until the separate FastAPI host is live, migrations are current, and the Netlify smoke test passes. The previous Vercel deployment path remains available and does not require `EVALIO_API_ORIGIN`.
