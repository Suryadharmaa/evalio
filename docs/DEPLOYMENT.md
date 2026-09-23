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

## Netlify frontend + separately hosted FastAPI

Netlify hosts the Next.js frontend, but does not deploy the Python `api/index.py` FastAPI app as a Netlify Function. Host the existing FastAPI ASGI app on a Python-capable service at a stable HTTPS origin. The frontend proxies `/api/v1/*` to that origin through the Next.js rewrite in `next.config.ts`; users continue to call the same-origin path. No production database import or deployment is performed by this repository configuration.

1. Deploy the FastAPI app using `api.index:app`, with a production Python environment and a Supabase production database. Apply `uv run alembic upgrade head` from a trusted job before accepting traffic. Check `https://<api-host>/api/v1/health` and `/api/v1/health/ready` (both must return HTTP 200).
2. Set backend `APP_ENV=production`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `IP_HASH_SALT`, `ALLOWED_HOSTS=<api-host>`, and `ALLOWED_ORIGINS=https://<site>.netlify.app` (plus your final custom HTTPS origin, if used). Set `GROQ_API_KEY` only on the backend if AI essay review is enabled. Never place backend secrets in Netlify `NEXT_PUBLIC_*` variables.
3. In Netlify, connect the repository as a Next.js project. `netlify.toml` sets build command `npm run build` and publish directory `.next`. Set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, and `EVALIO_API_ORIGIN=https://<api-host>` in Netlify environment variables. The latter must be an HTTPS origin without a trailing slash or path; a Netlify build fails if it is absent.
4. Add the Netlify and final custom domain redirect URLs to Supabase Auth. For each deploy context, use matching frontend/backend/database settings; never point a preview at production by accident.
5. Before release, run `uv run python scripts/production_smoke.py --base-url https://<site>.netlify.app`, sign in, open Dashboard and College Explorer, run a tool, and check `/api/v1/health/ready` through the Netlify URL. Repeat on the custom domain after DNS/TLS setup.

Do not launch until the separate FastAPI host is live, migrations are current, and the Netlify smoke test passes. The previous Vercel deployment path remains available and does not require `EVALIO_API_ORIGIN`.
