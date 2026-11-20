# Evalio UTBK — Academic Ambition UI design extension
Status: draft visual brief for Codex; source of truth remains `docs/evalio-DESIGN.md`.

## Objectives
Create a quiet, credible, aspirational learning experience for Indonesian Class 12 students. The exam UI is a work surface, not a promotional surface. The PTN explorer should evoke real university life through original or appropriately licensed campus imagery and readable evidence, without claiming official affiliation with any campus.

## Tokens (reuse existing Evalio identity)
Primary `#281950`, accent `#6757F5`, soft `#F2EFFF`, success `#168A5B`, warning `#B7791F`, danger `#C24A55`. Neutral cards, moderate radius, subtle borders, clear focus rings. Keep existing Evalio typography where licensed and available; use system-serif/system-sans fallbacks if not.

## Page-level tone
- Public landing: aspiration + explicit benefits + authentic campus photos; one primary CTA "Coba Tes Diagnostik".
- Dashboard: next action first, 7-subtest progress and 2 PTN targets; no overwhelming charts.
- Practice: passage and question, large touch targets, accessible options, optional explanation only after submitting.
- Full tryout: neutral canvas, steady timer, question palette, flag, autosave status, submit confirmation. No ads, confetti, leaderboard or disruptive motion.
- Results: raw counts, weak areas, evidence and recommended next practice; sample-size caveats.
- PTN explorer/planner: filters, clear source/year badges, program comparisons, data freshness, explicit unavailable states.
- Billing: transparent pricing, access duration, renewal terms, payment and refund information.

## Layout and behavior
Mobile-first 360–430px; desktop readable max-width; >=44px target size on touch controls; keyboard navigation and visible focus; semantic headings; color is never the only status cue; contrast and reduced-motion tested; use Indonesian plain-language labels. Use `KaTeX` for reliable math rendering, including screen reader alternatives where feasible.

## Components to reuse/build
Nav, CTA, status chip, source-year chip, question card, single/multi choice, math block, passage view, timer, question palette, autosave indicator, result summary, topic progress, PTN program card, source panel, comparison table, verification warning.
Build reusable UI primitives only where current `components/ui` cannot support them. Avoid global reskin.

## Assets and brand integrity
Never lift campus photos/logos from arbitrary pages without checking rights and terms. Do not imply Evalio is endorsed by SNPMB or a PTN. Provide accessible descriptive alt text. Avoid derivative/sham logos resembling official institutions.

## Token-efficient design workflow
1. Read only `docs/evalio-DESIGN.md`, this document, existing `app/globals.css` and relevant screen/component.
2. Sketch mobile + desktop hierarchy in a short note.
3. Build one page using existing primitives; take a screenshot through Playwright when browser is available.
4. Audit with web-design-guidelines skill if installed, and check keyboard/touch and focus.
5. Give visual review diff, not a global redesign.
