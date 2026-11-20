---
name: evalio-design
description: Use for Evalio UTBK frontend design, exam screens, responsive dashboard, accessibility audits or PTN explorer visual components.
---
# Evalio Academic Ambition — design skill
First read `docs/evalio-DESIGN.md` (existing brand) and `docs/utbk/DESIGN_SYSTEM.md` (UTBK extension). Only then inspect relevant components.

## Rules
- Preserve Evalio palette: #281950, #6757F5, #F2EFFF; restrained academic feel.
- Calm and credible, mobile-first for Indonesian students, no generic AI neon styling.
- Full exam screen has no ads, confetti, invasive popups, or distracting hero art.
- Prioritize accessible radio options, keyboard navigation, screen reader labels, source/year chips, server-save indicator.
- Readable maths using approved renderer with text alternatives; verify equations and wrapping on narrow screens.
- Use real campus photos only if appropriately licensed; never imply official SNPMB/PTN endorsement.
- Reuse current UI primitives; do not reskin all app routes.
- UI plan -> implement one screen -> focused screenshot/a11y audit -> concise diff and tests.

## Delivery
Explain layout hierarchy and mobile behavior; include tested widths and any unverified visual states. No unapproved production deployment.
