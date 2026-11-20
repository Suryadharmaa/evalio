# Dependencies, Codex skills, and GitHub tools — adoption plan
Status: planning, not an installation record. Avoid conflating Codex Plugins, Agent Skills, npm/python packages and external integrations.

## Mandatory for implementation (existing, no download unless cloud setup installs them)
- Connected GitHub repo for Codex Cloud; `Suryadharmaa/evalio`.
- Node >=20.9 (recommended Node 22), npm with lockfile: `npm ci`.
- Python 3.12 + uv: `uv sync --frozen`.
- Existing Next.js 16/React 19/TypeScript/Tailwind 4, FastAPI/Python, Supabase auth/DB, Alembic, Zod/Pydantic, Vitest, Playwright, Ruff/MyPy. Verify package versions before making changes.
- Existing GitHub Actions CI; no new CI service required.

## External coding Agent Skills (recommendation, not mandatory system plugins)
1. **UI/UX Pro Max**, github.com/nextlevelbuilder/ui-ux-pro-max-skill — for early design exploration ONLY. After reviewing third-party source, install per project (inside Codex cloud workspace): `npx ui-ux-pro-max-cli init --ai codex`. Review generated files before committing. Better: commit a concise custom Evalio design skill once final style decided, so each cloud task does not need to download it.
2. **Vercel react-best-practices**, github.com/vercel-labs/agent-skills — optional for frontend tasks; install only after verifying skill CLI availability: `npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices` (inspect live available skill identifier; repository name can differ from display label).
3. **Vercel web-design-guidelines**, github.com/vercel-labs/agent-skills — optional for UI/accessibility review: `npx skills add vercel-labs/agent-skills --skill web-design-guidelines`.
4. **OpenAI official Plugins / Skills docs**, github.com/openai/plugins and developers.openai.com/plugins/concepts/skills — reference for internal skill formatting, no plugin install necessary.
Do not invoke all skills in every task. Do not confuse Claude marketplace `/plugin` commands with Codex commands.

## Project-owned skills (commit into repo; reusable and stable)
- `.agents/skills/evalio-utbk-engine/SKILL.md`: exam blueprint, answer protection, deterministic scoring, concurrency.
- `.agents/skills/evalio-ptn-data/SKILL.md`: authoritative source tracking, year versioning, no fake passing grade.
- `.agents/skills/evalio-design/SKILL.md`: Evalio purple design tokens, educational UX, exam focus.
These are scoped to the repository; no separate package installer necessary.

## Proposed application additions (add ONLY in feature ticket)
- `katex`: math rendering; optionally `react-katex` if compatibility and licence verified, otherwise a small safe renderer.
- `@tanstack/react-table`: only if PTN sorting/filter complexity requires it; native table may suffice for alpha.
- `recharts`: only after simple result cards prove useful.
- shadcn/ui: optional source-managed components, not mandatory; avoid replacing existing UI.
- Tiptap: deferred until editor complexity justifies it.
- Monitoring and analytics: initially use existing app logs/CI; introduce privacy-conscious analytics later.

## External providers (NOT npm plugins; secrets controlled)
- Supabase: already used. Use **separate development project** with schema migrations, RLS and limited roles.
- Indonesian gateway such as Midtrans/Xendit: integrate after paid beta readiness and terms; choose one based on verified fees and contracts.
- PTN/SNPMB/PDDikti official sources: source-backed catalog; **do not assume public API or automatic commercial data reuse permission**.
- GitHub Actions: review PR tests and branch protection if enabled.

## Exact cloud install workflow
```bash
# Run in the Codex Cloud repo workspace, NOT on the laptop:
bash scripts/codex-cloud-setup.sh

# For a narrowly scoped UI research task only, after source review:
npx ui-ux-pro-max-cli init --ai codex
npx skills add vercel-labs/agent-skills --skill web-design-guidelines

# For new math module implementation, in a separate feature PR:
npm install katex
```

## Install policy
Never run unreviewed install scripts with production credentials. Keep package-lock.json and uv.lock under version control; no `npm install -g` required. Skill installers may depend on network access and are NOT part of the deterministic CI build. Do not insert arbitrary MCP servers into cloud env or give them broad repository/production permissions.

## References
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- https://github.com/vercel-labs/agent-skills
- https://github.com/openai/plugins
- https://developers.openai.com/plugins/concepts/skills
- https://help.openai.com/en/articles/20001545-using-codex-cloud
