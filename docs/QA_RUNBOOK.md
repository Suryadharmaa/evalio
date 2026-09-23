# Evalio Production QA Runbook

Run after preview deployment and again after production deployment.

## Automated gates

```text
npm ci
npm run lint
npm run typecheck
npm test
npm run test:e2e
npm run build
uv sync --frozen
uv run ruff check .
uv run ruff check api scripts --select S
uv run mypy
uv run pytest
uv run coverage run --source=api/admission_engine/engine -m pytest tests/python
uv run coverage report --fail-under=90
npm audit --audit-level=low
uvx pip-audit
uv run python scripts/production_smoke.py https://preview.example.com
```

## Manual release smoke

- Anonymous essay: submit, inspect score/components/issues, refresh, confirm no saved draft.
- Authentication: magic-link sign-in and sign-out.
- Profile: create, edit, reload, confirm owner-only persistence.
- Academics, activities, honors: enter fixtures and inspect explanations.
- College explorer: search/filter, open detail, inspect sources and freshness.
- College evaluation: verify separate alignment, selectivity, requirements, financial, confidence, and planning cards.
- Application audit: verify required/optional, completeness/quality, deadlines, and priorities remain separate.
- Report: render printable view and confirm no raw private text duplication.
- Export: verify only current user's content.
- Delete: confirm explicit phrase, transaction completion, and inability to retrieve deleted content.
- Mobile: execute core workflows at 360×800, 390×844, and 768×1024 without horizontal scrolling.
- Accessibility: keyboard-only flow, focus order, labels/errors, heading hierarchy, dialogs, reduced motion, contrast, and non-color score status.

Release only when all P0/P1 issues are resolved.
