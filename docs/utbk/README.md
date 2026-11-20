# Evalio UTBK 2027 — Cloud Development Pack
Version 1.0 draft | 2026-11-20 | This pack is **planning and workflow documentation**, not a shipped UTBK feature.

## Start here
1. `PRD.md`: users, value proposition, MVP and commercial hypotheses.
2. `ARCHITECTURE_AND_DATA.md`: backend/domain boundaries, DB entities, scoring and access controls.
3. `DESIGN_SYSTEM.md`: PTN-inspired Academic Ambition visual direction, compatible with existing `docs/evalio-DESIGN.md`.
4. `CODEX_CLOUD_RUNBOOK.md`: configure Codex Cloud and GPT-6.1 Sol Medium; do not need a local development machine.
5. `DEPENDENCIES_AND_SKILLS.md`: what's required, what exists, optional third-party skills, project skills and installation policy.
6. `TASK_BOARD.md`: small PR-oriented tickets EVAL-001..EVAL-020.
7. `TEST_AND_CONTENT_QA.md`: security, reliability and editorial acceptance.
8. `CODEX_PROMPTS.md`: starter prompts for scoped Codex Cloud tasks.

## Active project-owned skills
- `.agents/skills/evalio-utbk-engine/SKILL.md`
- `.agents/skills/evalio-ptn-data/SKILL.md`
- `.agents/skills/evalio-design/SKILL.md`

## Safe bootstrap
- Review this PR before merging.
- In Codex Cloud, connect `Suryadharmaa/evalio` with the approved environment.
- Set setup command to `bash scripts/codex-cloud-setup.sh` when script available on selected branch.
- Start with **EVAL-001 read-only audit** using `CODEX_PROMPTS.md`.
- Do not install payment connectors or use production keys at bootstrap.
- Existing international admissions is in scope for regression checks, not a rebrand.
- Verify official 2027 rules before marketing any exam blueprint as official.

## Founder responsibilities (cannot be delegated to code alone)
Verify school/user feedback, pricing, content authorship and licensing, PTN data reuse permissions, payment merchant eligibility, privacy disclosures/consent, acceptance criteria, live deployment and funding decisions.

## Research links
- https://www.snpmb.id/utbk-snbt/informasi-umum
- https://snpmb.id/fr/
- https://www.snpmb.id/utbk-snbt/daya-tampung-snbt
- https://help.openai.com/en/articles/20001545-using-codex-cloud
- https://github.com/openai/plugins
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- https://github.com/vercel-labs/agent-skills
