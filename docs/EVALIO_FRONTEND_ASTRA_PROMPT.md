# Evalio Frontend — Astra Master Implementation Prompt

You are working inside the existing **Evalio** repository.

Your job is to redesign and implement the frontend so it becomes **memorable, animated, interactive, product-driven, premium, and distinctly Evalio**, while preserving all existing backend contracts, routes, deterministic scoring logic, privacy constraints, and database semantics.

This is an **in-place frontend refinement**, not a greenfield rebuild.

---

## 1. Read before coding

Before changing anything, inspect the repository and read the current project documentation, especially:

- `docs/PRD.md`
- `docs/TECHNICAL_DESIGN.md`
- `docs/API_SPEC.md`
- `docs/DATA_SPEC.md`
- `docs/SCORING_SPEC.md`
- `docs/RULEBOOK.md`
- `docs/SECURITY.md`
- `docs/TEST_PLAN.md`
- `docs/UI_UX.md`
- `docs/UI_UX_SPEC.md`
- `docs/TOOLS_SPEC.md`
- `docs/evalio-DESIGN.md` if present
- `AGENTS.md` if present

If old UI specs conflict with the newer Evalio-specific design spec, the newer Evalio-specific frontend direction wins.

Do not change scoring formulas, admissions logic, data ownership, security rules, or backend semantics for visual convenience.

---

## 2. Product identity

Product: **Evalio**

Core tagline:

> **Every score has a reason.**

Core analytical interaction:

> **Score → Evidence → Rule → Explanation**

Core design identity:

> **Editorial outside + quantitative inside + transparent everywhere.**

Evalio should feel:

- calm;
- premium;
- analytical;
- highly interactive;
- editorial;
- student-friendly;
- source-aware;
- credible;
- modern;
- evidence-first.

Evalio must NOT feel like:

- a generic AI SaaS template;
- a neon “AI startup”;
- a clone of Test Ninjas;
- a clone of Esslo;
- an empty white Tailwind landing page;
- a chance calculator with fake precision.

---

## 3. External UX references

Use these only as **high-level inspiration for pacing, visual hierarchy, density, product presentation, interaction quality, and memorability**:

### Test Ninjas

- `https://test-ninjas.com/`
- `https://test-ninjas.com/college`
- `https://test-ninjas.com/college-essay-editor`
- `https://test-ninjas.com/college-admissions-chances`
- `https://test-ninjas.com/college-profiles`

Study these traits:

- product-first hero sections;
- strong visual rhythm;
- dense but readable tool sections;
- large product previews;
- compact stats and proof strips;
- intentional CTA hierarchy;
- useful metadata inside cards;
- direct routes into tools;
- real UI previews instead of decorative illustrations.

### Esslo

- `https://www.esslo.org/`

Study these traits:

- memorable hero;
- friendly but premium tone;
- large interface preview;
- simplified user journey;
- warmth without visual clutter;
- confident typography.

Do **not** copy their branding, copywriting, source code, screenshots, proprietary datasets, exact layouts, or assets.

The output must still be unmistakably **Evalio**.

---

## 4. Existing stack and architecture

Evalio uses approximately:

- Next.js
- React
- TypeScript
- Vercel
- FastAPI under `api/`
- Supabase Auth/PostgreSQL
- Zod frontend validation

Expected high-level structure:

```text
admission-engine/
├── app/
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
├── tests/
└── docs/
```

Do not assume this blindly. Inspect the actual repo first.

Do not create duplicate component systems such as:

```text
components-v2/
frontend-new/
redesign-components/
```

Reuse and refactor existing components whenever possible.

---

## 5. Visual system

Preserve the current Evalio premium-minimal base and make it more distinctive.

Use these semantic colors unless the repo already defines equivalent tokens:

```text
Evalio Ink          #281950
Evalio Violet       #6757F5
Soft Lavender       #F2EFFF
Evalio Border       #D9D3F0
Background          #FFFFFF
Muted Text          #686082
Success             #168A5B
Warning             #B7791F
Danger              #C24A55
```

Do not scatter raw hex colors through components.

Map them into the existing token system:

```text
--background
--foreground
--primary
--primary-foreground
--surface-soft
--border
--muted
--muted-foreground
--success
--warning
--danger
```

---

## 6. Typography

Preserve the serif + sans split.

Use serif for:

- hero statements;
- large section headings;
- editorial/methodology moments;
- final CTA statements.

Use sans-serif for:

- forms;
- navigation;
- score cards;
- metrics;
- evidence;
- source metadata;
- tables;
- controls.

The visual message should be:

> **admissions publication × analytical software**

Do not make all typography look like a generic geometric SaaS dashboard.

---

## 7. Fix contrast bugs before redesign

Audit the entire frontend for text/background contrast bugs.

Known issue: primary CTA labels such as `Evaluate my application` can render with dark/black text and visually disappear.

Fix this at the shared component/token level, not with page-specific hacks.

### Primary button

```text
background: Evalio Violet
foreground: white
```

The foreground must remain white in:

- default;
- hover;
- active;
- focus;
- disabled states where appropriate.

Never allow `text-black` or inherited foreground to override it.

### Secondary button

```text
background: white
foreground: Evalio Ink
border: Evalio Border
```

### Dark-section button

Either:

```text
white background + Evalio Ink text
```

or:

```text
Evalio Violet background + white text
```

### Ghost button

Light surface → Evalio Ink text.

Dark surface → white text.

Audit every shared button/link/tab/chip state.

Target WCAG 2.2 AA minimum.

---

## 8. Remove the “template” feel

The current frontend should stop feeling:

- too empty;
- overly safe;
- repetitive;
- generic;
- like every section is a white rounded card;
- visually unfinished.

Create **controlled information density**.

Do not solve emptiness with decorations.

Use product information as the visual interest:

- score breakdowns;
- confidence labels;
- source freshness;
- issue counts;
- evidence snippets;
- methodology links;
- rule IDs;
- verified-source chips;
- realistic product UI;
- campus imagery where licensed.

---

## 9. Evalio signatures

These should recur across the product.

### Section eyebrow

Examples:

```text
EVALIO / APPLICATION ANALYSIS
EVALIO / ESSAY
EVALIO / COLLEGE DATA
EVALIO / METHODOLOGY
EVALIO / COURSEWORK
```

Style: small, uppercase, semibold, tracked, violet.

### Confidence

```text
● HIGH CONFIDENCE
● MEDIUM CONFIDENCE
● LOW CONFIDENCE
```

Always use text + color, not color alone.

### Provenance

```text
Verified source
2026–27 cycle
Updated Sep 2026
```

### Evidence interaction

A scored result should support:

```text
Score
→ Evidence
→ Rule
→ Explanation
```

Use accordion, drawer, expandable row, side panel, or popover depending on context.

---

## 10. Motion language

Make Evalio memorable through subtle, deliberate motion.

Suggested timings:

```text
micro       120–160ms
base        180–220ms
section     280–420ms
```

Suggested easing:

```text
cubic-bezier(0.4, 0, 0.2, 1)
```

Good motion:

- fade + 8–16px translate for meaningful section entrance;
- staggered tool-card reveal;
- score-number reveal;
- score-bar fill;
- subtle hover elevation;
- arrow translation 2–4px;
- underline reveal;
- animated tab indicator;
- filter chip transition;
- evidence drawer expansion;
- subtle campus-image zoom;
- mild hero background movement;
- count animation when it represents actual state.

Avoid:

- bouncing everything;
- looping floating blobs;
- heavy parallax;
- dramatic springs;
- constant animated gradients;
- fake progress percentages;
- effects that delay reading.

Respect `prefers-reduced-motion`.

If a motion library already exists, use it. If none exists and a small dependency materially improves the implementation, prefer a lightweight production React motion library. Do not convert the whole site to client components only for animation.

---

# 11. Homepage

Redesign the existing homepage in place.

## Hero

Desktop structure:

```text
LEFT
editorial headline
supporting copy
primary CTA
secondary CTA
trust microcopy

RIGHT
large interactive Evalio product preview
```

Suggested content structure:

```text
EVALIO / APPLICATION ANALYSIS

Know where your
application stands.

Transparent analysis across academics,
activities, essays, and college fit.

[ Evaluate my application → ]
[ Analyze an essay ]

Every score has a reason.
```

Product preview:

```text
APPLICATION STRENGTH

84 / 100        ● HIGH CONFIDENCE

Academics             91
Activities            84
Essay                 81
Honors                76

3 priority findings

View evidence →
```

Interaction:

- animate score bars once;
- hover metric → emphasize associated row/bar;
- click `View evidence` → reveal a compact evidence panel;
- no random changing score values.

The preview should look like real Evalio UI, not a fake browser screenshot.

## Hero background

Do not use generic neon gradients.

Prefer:

- white/cream canvas;
- very subtle lavender radial illumination;
- faint grid/editorial lines;
- restrained violet accent.

## Trust strip

Use strong product facts, not weak decorative stats.

Example:

```text
100%
Explainable scoring

0
AI models required

Versioned
Methodology

Source-aware
College data
```

Keep it compact and animated only on first viewport entry.

---

## Tools section

Do not make six identical cards.

Use an asymmetric editorial layout:

```text
LARGE FEATURED
Application Evaluator

MEDIUM
Essay Evaluator

MEDIUM
College Explorer

SMALL
GPA Toolkit

SMALL
Coursework

SMALL
Scholarships
```

Tool cards should include useful metadata:

```text
8 dimensions
Rule-based
Source-backed
4 academic components
```

Hover:

- border emphasis;
- subtle elevation;
- arrow shift;
- icon shift 1–2px;
- optional extra metadata reveal.

No dramatic tilt.

---

## Methodology section

This is a signature Evalio section.

Headline:

```text
Nothing hidden
behind the score.
```

Preview:

```text
ACADEMIC STRENGTH

91

Performance         45%
Course rigor        30%
Trend               10%
Context             10%
Major prep           5%

5 components
12 rules
● HIGH CONFIDENCE

View evidence →
```

Clicking `View evidence` reveals:

```text
EVIDENCE
Academic trend
+4.2 points across four terms

RULE
ACAD-003

EFFECT
+6.5 points
```

---

## College-fit section

Use a dark Evalio Ink section for pacing.

```text
EVALIO / COLLEGE FIT

Fit without
fake certainty.
```

Product card:

```text
Bowdoin College

Academic Alignment      STRONG
Selectivity Risk        VERY HIGH
Requirements            COMPATIBLE
Financial Fit           STRONG

PLANNING CATEGORY
HIGH REACH

Why this result? →
```

No admission percentage.
No probability pie chart.

`Why this result?` should expand a concise explanation.

---

## College-data preview

Add a polished mini College Explorer preview.

Show 3–5 institutions with:

- school name;
- location;
- testing policy;
- international-aid status;
- current-cycle/source chip;
- campus image if verified.

If media is missing, use a deliberate branded fallback rather than broken imagery.

Never hotlink random images.

---

## Final CTA

Do not use a generic empty centered card.

Use a strong editorial ending:

```text
Every score has a reason.

Start with your application,
your essay, or a college.

[ Evaluate my application → ]
[ Explore colleges ]
```

Use a strong background block and restrained visual detail.

---

# 12. Navigation

Public navigation:

```text
Evalio

Tools ▾
Colleges
Methodology

Sign In
Get Started →
```

Desktop Tools dropdown:

```text
ESSAYS
Essay Evaluator
Writing Pattern Checker
Essay Idea Builder

APPLICATION
Application Evaluator
GPA Toolkit
Coursework Evaluator
Activity Evaluator
Scholarship Tracker

LETTERS
LOR Builder
LOR Evaluator
```

Use short descriptions and a polished mega/dropdown panel.

Mobile: use accessible disclosure/accordion navigation.

No hover-only mobile behavior.

---

# 13. College Explorer

Route:

```text
/colleges
```

Make it feel like a real discovery product.

Header:

```text
Explore colleges.

[ Search Harvard, Bowdoin, Stanford... ]
```

Filters:

```text
Country
State
Testing
International aid
Institution type
Application platform
```

Use compact chips/popovers with animated selected states.

Do not render a giant static form.

## College card

Show:

- real campus image when verified;
- school name;
- city/state;
- institution type;
- testing policy;
- international-aid status;
- source/freshness chip.

Hover:

- image scale about 1.02;
- subtle border/elevation change;
- CTA arrow shift.

## College detail

Route:

```text
/colleges/[slug]
```

Use a memorable visual header:

```text
campus hero image
school name
location
school type

Verified source
2026–27 cycle
```

Use sectional tabs/sticky navigation:

```text
Overview
Admissions
Testing
Requirements
International
Financial Aid
Costs
Sources
```

Where a value is missing, show:

```text
Not yet verified
```

Do not treat `0`, `null`, and `UNKNOWN` as equivalent.

---

# 14. Essay Evaluator

Route:

```text
/tools/essay-evaluator
```

Make it feel like a real writing workspace.

Desktop:

```text
LEFT 65%
editor / prompt / word count

RIGHT 35%
score / dimensions / findings
```

Mobile: stack cleanly.

Editor:

- calm white surface;
- strong focus state;
- collapsible prompt;
- sticky word count;
- clear CTA.

Result:

```text
MECHANICAL ESSAY SCORE
81 / 100
● HIGH CONFIDENCE
```

Dimensions:

```text
Compliance
Clarity
Structure
Specificity
Reflection Signals
Voice Indicators
Sentence Variety
Style Hygiene
```

Interactive findings:

- expand `Why this matters`;
- show evidence;
- show rule ID unobtrusively;
- highlight relevant sentence/evidence when current API data supports it.

Do not change scoring logic.

---

# 15. Writing Pattern Checker

Route:

```text
/tools/writing-pattern-checker
```

Never display AI-authorship probability.

Result:

```text
WRITING PATTERN RISK
MODERATE

7 / 24 signals triggered
```

Use grouped signal rows, evidence drawers, and simple deterministic visualizations.

Keep the disclaimer visible but not visually dominant.

---

# 16. Application Evaluator

Route:

```text
/tools/application-evaluator
```

This should be one of the most polished surfaces.

Top:

```text
Target college
[ Search/select ]

Use saved profile ✓
```

Result:

```text
APPLICATION STRENGTH
84

Academic Alignment
Course Rigor
Activities
Honors
Testing

Selectivity Risk
Requirements
Financial Fit
Data Confidence

PLANNING CATEGORY
HIGH REACH
```

Use progressive disclosure, evidence, confidence, source links, and animated score rows.

No exact admission probability.

---

# 17. GPA Toolkit

Route:

```text
/tools/gpa
```

Tabs:

```text
High School GPA
Weighted
Unweighted
Cumulative
Percentage
International
```

Interactions:

- smooth add/remove course rows;
- light animation when totals change;
- formula/methodology drawer;
- no awkward full-page reload.

International mode remains first-class.

Do not force 4.0 conversion.

---

# 18. Coursework Evaluator

Route:

```text
/tools/coursework-evaluator
```

Group course inputs by grade level.

Use level badges:

```text
Regular
Honors
AP
IB
Dual Enrollment
Advanced
```

Result:

```text
COURSE RIGOR
88 / 100

Challenge Level
Core Coverage
Advanced Utilization
Progression
Major Preparation
```

Context callout example:

```text
No AP/IB courses available
No penalty applied.
```

---

# 19. Scholarship Tracker

Route:

```text
/tools/scholarships
```

Public discovery:

- search;
- international eligibility;
- award amount;
- deadline;
- need/merit;
- major.

Authenticated tracker:

```text
Saved
Researching
Applying
Submitted
Finalist
Won
Rejected
Expired
```

Use a polished list/board toggle only if it fits the existing architecture.

Deadline urgency must use text + color.

---

# 20. LOR tools

## LOR Builder

Route:

```text
/tools/lor-builder
```

Use progressive sections:

```text
Relationship
Evidence
Comparative context
Endorsement
```

Output should look like a structured framework, not chat text.

## LOR Evaluator

Route:

```text
/tools/lor-evaluator
```

Mirror Essay Evaluator visual language for consistency.

---

# 21. Dashboard

If `/dashboard` exists, make it the product center.

Avoid a generic grid of unrelated cards.

Suggested composition:

```text
Welcome / next action
Application Strength summary
Priority findings
Target colleges
Application completeness
Essay status
Upcoming deadlines
```

Primary pathways:

```text
Continue profile
Analyze essay
Evaluate college
Explore scholarships
```

Use actual user data only.

---

# 22. Shared components

Inspect current components before adding anything.

Likely reusable primitives belong under the existing `components/ui/` system.

Evalio-specific reusable components should live in the existing evaluation/product organization, for example:

```text
components/evaluation/
  ScoreCard
  ScoreBreakdown
  ScoreBar
  ConfidenceBadge
  RuleFinding
  EvidencePanel
  MethodologyLink
  SourceBadge
  FreshnessBadge
  PlanningCategory
  PriorityFinding
```

Other likely shared components:

```text
SiteHeader
SiteFooter
ToolsMenu
SectionEyebrow
ProductPreview
ToolCard
CollegeCard
CollegeHero
SourceProvenance
```

Do not create duplicates if equivalent components already exist.

---

# 23. Component state quality

Every reusable interactive component must define:

- default;
- hover;
- focus-visible;
- active;
- disabled;
- loading where relevant;
- error where relevant;
- dark-surface variant where relevant.

Buttons must never depend on accidental inherited text color.

Use at least three presentation modes across the product:

```text
open/editorial
surface/card
contrast/dark
```

Do not make the entire interface one endless card grid.

---

# 24. Microinteractions

Implement meaningful interactions consistently.

### Links

`View evidence →`

Hover:

- arrow moves 3px;
- subtle underline/opacity change.

### Score row

Hover:

- soft lavender background;
- slightly stronger bar;
- pointer only if clickable.

### Tool card

Hover:

- violet border emphasis;
- subtle elevation;
- arrow/icon movement.

### College card

Hover:

- image scale 1.02;
- subtle surface lift;
- no 3D rotation.

### Tabs

Animated indicator.

### Filter chips

Smooth selected state.

### Accordion / evidence drawer

Smooth expansion, accessible focus behavior.

### CTA

Small translation/elevation only.

---

# 25. Scroll behavior

Viewport reveals should be selective.

Good candidates:

- hero preview;
- trust strip;
- tools group;
- methodology visual;
- college-fit section;
- final CTA.

Do not animate every paragraph.

Do not make users wait for content to appear while quickly scrolling.

---

# 26. Loading, empty, and error states

Prefer structure-aware skeletons to generic spinners.

Examples:

- college-card skeleton;
- evaluation-result skeleton;
- dashboard-summary skeleton;
- scholarship-list skeleton.

No fake progress percentages.

Useful empty state example:

```text
No colleges match these filters.

Try removing Test Optional or expanding the state filter.

[ Clear filters ]
```

Useful error example:

```text
College data is temporarily unavailable.

Your profile has not been changed.

[ Try again ]
```

Never expose stack traces.

---

# 27. Campus imagery

Use backend/media data when available.

Requirements:

- real campus imagery only when source/licensing data permits;
- alt text;
- responsive image sizing;
- graceful fallback;
- no random Google Images hotlinks;
- no unsourced imagery.

Fallback can use a branded Evalio editorial panel with initials/location.

---

# 28. Accessibility

Target WCAG 2.2 AA.

Mandatory:

- full keyboard navigation;
- visible focus;
- semantic buttons/links;
- accessible form labels;
- no color-only status;
- 44×44 mobile touch targets where practical;
- reduced-motion support;
- usable at 360px;
- accessible dialogs/drawers;
- meaningful alt text;
- no essential hover-only information.

Animation must never reduce accessibility.

---

# 29. Mobile

Treat mobile as a real product experience.

At 360–430px:

- hero becomes single-column;
- preview remains readable;
- CTAs may stack;
- tools dropdown becomes disclosure navigation;
- score cards fit width;
- tables become cards/rows;
- filters use bottom sheet/drawer where appropriate;
- no horizontal overflow;
- motion is lighter.

---

# 30. Performance

Maintain strong Core Web Vitals.

Do not:

- ship huge animation bundles unnecessarily;
- eagerly load all campus images;
- introduce CLS-heavy animation;
- add hero autoplay video;
- disable Next image optimization without reason;
- make the whole app client-side just for effects.

Use server components where appropriate and client components only for actual interactivity.

---

# 31. Preserve routes

Do not break current routes.

Expected routes include approximately:

```text
/
/essay
/activity-analyzer
/colleges
/colleges/[slug]
/methodology
/privacy
/terms

/tools/essay-evaluator
/tools/writing-pattern-checker
/tools/essay-idea-builder
/tools/application-evaluator
/tools/gpa
/tools/coursework-evaluator
/tools/activity-evaluator
/tools/scholarships
/tools/lor-builder
/tools/lor-evaluator

/dashboard
/profile
/profile/academics
/profile/testing
/profile/activities
/profile/honors
/essays
/essays/[id]
/colleges/compare
/targets
/application/[collegeId]
/reports
/settings
```

Use the actual repo routes if they differ.

Do not create duplicate route variants.

---

# 32. Frontend/backend boundary

Do not move authoritative scoring into React.

Frontend may handle:

- presentation;
- animation;
- display formatting;
- UI state;
- presentation-only sorting/filter state.

Backend remains authoritative for:

- scores;
- rules;
- planning categories;
- financial-fit logic;
- persistence;
- provenance;
- private data access.

---

# 33. No fake content

Do not fabricate:

- student testimonials;
- applicant outcomes;
- fake university partners;
- fake user counts;
- fake acceptance probabilities;
- fake scholarships;
- fake admitted-student profiles.

Marketing previews may use clearly illustrative static UI values, but must not imply they represent real user outcomes.

Do not use claims such as:

```text
90,000 students
12,000 admitted profiles
Stanford 72%
```

unless Evalio has verified supporting data.

---

# 34. Copy style

Preferred Evalio copy:

```text
Every score has a reason.
Know where your application stands.
See the evidence behind every score.
Nothing hidden behind the score.
Fit without fake certainty.
Source-backed college data.
Admissions analysis you can inspect.
Clearer evidence. Better decisions.
```

Avoid generic startup copy:

```text
Unlock your full potential
Supercharge your admissions journey
Revolutionary AI-powered insights
Get into your dream school guaranteed
```

---

# 35. Implementation sequence

Do the work in this order.

## Phase 1 — Audit

Inspect:

1. routes;
2. existing components;
3. global CSS/theme;
4. Tailwind/design tokens;
5. button variants;
6. animation dependencies;
7. API hooks;
8. current responsive behavior.

Create a concise internal implementation plan and continue automatically unless genuinely blocked.

## Phase 2 — Foundation

Fix/refine:

- color tokens;
- typography hierarchy;
- button variants;
- focus states;
- spacing/container primitives;
- card primitives;
- animation utilities;
- badges/evidence/source components.

## Phase 3 — Homepage

Implement the full redesigned homepage.

## Phase 4 — Core product surfaces

Prioritize:

1. College Explorer
2. College Detail
3. Application Evaluator
4. Essay Evaluator
5. Dashboard

Then apply the same design system to the remaining tools.

## Phase 5 — Motion pass

Only after hierarchy/layout are strong.

## Phase 6 — QA

Verify:

```text
360px
390px
768px
1024px
1440px+
```

---

# 36. Acceptance criteria

The task is complete only when all are true.

## Brand

- [ ] Clearly feels like Evalio.
- [ ] Does not look like a Test Ninjas clone.
- [ ] Does not look like an Esslo clone.
- [ ] Evidence/confidence/source patterns recur consistently.
- [ ] `Every score has a reason` is expressed through interaction, not just text.

## Visual quality

- [ ] Homepage no longer feels empty/template-like.
- [ ] Section rhythm is varied.
- [ ] Cards are not monotonously identical.
- [ ] Product UI creates visual interest.
- [ ] Dark/light pacing is intentional.
- [ ] Typography feels editorial and premium.

## Interaction

- [ ] Hero has meaningful interaction.
- [ ] Score/evidence previews react or expand.
- [ ] Tool cards have polished hover/focus behavior.
- [ ] College cards are interactive.
- [ ] Filters feel responsive.
- [ ] Tabs/accordions/drawers animate smoothly.

## Contrast

- [ ] Primary buttons always use readable white foreground.
- [ ] `Evaluate my application` is readable in all states.
- [ ] Dark-section buttons are readable.
- [ ] Ghost/outline states are correct.
- [ ] No text disappears into its background.

## Product integrity

- [ ] No fake admission probability.
- [ ] No fake applicant profiles/testimonials.
- [ ] No AI-authorship probability.
- [ ] No frontend scoring duplication.
- [ ] Source/freshness data preserved.
- [ ] Unknown/null data remains honest.

## Accessibility

- [ ] Keyboard usable.
- [ ] Focus visible.
- [ ] Reduced motion works.
- [ ] 360px works.
- [ ] No essential hover-only content.
- [ ] No color-only statuses.

## Engineering

- [ ] Existing routes preserved.
- [ ] Backend contracts preserved unless a backward-compatible addition is truly needed.
- [ ] Reusable components used.
- [ ] No duplicate component system.
- [ ] TypeScript passes.
- [ ] Frontend tests pass.
- [ ] Production build passes.

---

# 37. Final verification

Before stopping:

1. run frontend tests;
2. run TypeScript typecheck;
3. run lint;
4. run production build;
5. inspect browser console warnings/errors;
6. inspect responsive layouts;
7. inspect all button variants;
8. inspect keyboard focus;
9. inspect reduced-motion behavior;
10. inspect git diff.

If Playwright exists, run relevant E2E tests.

If visual-regression tests exist, update them only when the visual change is intentional.

---

# 38. Final response format

When implementation is complete, report only what was actually done:

```text
1. What changed
2. Main components modified
3. New reusable components
4. Routes redesigned
5. Motion/interactions added
6. Accessibility fixes
7. Contrast/button bugs fixed
8. Tests/typecheck/build results
9. Remaining frontend limitations
```

---

# Final direction

Do not make Evalio memorable by adding decoration.

Make it memorable because **the analytical product itself becomes the visual identity**.

Think:

```text
Test Ninjas
→ energy, density, product-forward presentation

Esslo
→ warmth, simplicity, memorable hero/interface preview

Evalio
→ editorial authority
  + interactive evidence
  + confidence
  + source provenance
  + calm premium motion
```

The finished frontend should feel like a polished admissions product a student remembers after seeing it once.

Inspect the existing repository, implement the frontend refinement in-place, test it thoroughly, and stop only when the acceptance criteria are satisfied.
