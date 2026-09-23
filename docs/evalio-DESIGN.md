---
version: alpha
name: Evalio
description: "A premium, evidence-first admissions interface based on the existing Fly-style foundation, preserving its restrained layout, 4px spacing system, serif/sans typography split, and motion while adding unmistakable Evalio branding."
sourceReference: "Adapted from the provided Fly.io-based design reference for Evalio."

brand:
  tagline: "Every score has a reason."
  principle: "Score → Evidence → Rule → Explanation"
  eyebrowPattern: "EVALIO / {CONTEXT}"
  tone: "calm, analytical, editorial, transparent, student-friendly"

colors:
  primary: "#281950"
  on-primary: "#ffffff"
  background: "#ffffff"
  surface: "#6757f5"
  surface-soft: "#f2efff"
  border: "#d9d3f0"
  text: "#281950"
  text-muted: "#686082"
  accent: "#6757f5"
  success: "#168a5b"
  warning: "#b7791f"
  danger: "#c24a55"
  confidence-high: "#168a5b"
  confidence-medium: "#b7791f"
  confidence-low: "#8c6673"
  verified: "#168a5b"

buttons:
  primary:
    background: "#6757f5"
    text: "#ffffff"
    border: "#6757f5"
  secondary:
    background: "#ffffff"
    text: "#281950"
    border: "#d9d3f0"
  ghost:
    background: "transparent"
    text: "#281950"
    border: "transparent"
  dark-section:
    background: "#ffffff"
    text: "#281950"
    border: "#ffffff"

typography:
  display:
    fontFamily: "Mackinac, ui-serif, Georgia, Cambria, Times New Roman, Times, serif"
    fontSize: 48px
    fontWeight: 575
    lineHeight: 1.3
    letterSpacing: -1.2px
  heading:
    fontFamily: "Mackinac, ui-serif, Georgia, Cambria, Times New Roman, Times, serif"
    fontSize: 40px
    fontWeight: 575
    lineHeight: 1.3
    letterSpacing: -1px
  body:
    fontFamily: "Fricolage Grotesque, ui-sans-serif, system-ui, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji"
    fontSize: 15px
    fontWeight: 450
    lineHeight: 1.66
  data:
    fontFamily: "Fricolage Grotesque, ui-sans-serif, system-ui, sans-serif"
    fontWeight: 550
    letterSpacing: -0.2px
  eyebrow:
    fontFamily: "Fricolage Grotesque, ui-sans-serif, system-ui, sans-serif"
    fontSize: 11px
    fontWeight: 650
    letterSpacing: 1.4px
    textTransform: "uppercase"

spacing:
  base: 4px
  scale: [4, 8, 12, 16, 20, 24, 32, 40, 48, 64]

radius:
  sm: 4px
  md: 8px
  lg: 10px
  xl: 16px
  pill: 9999px

shadows:
  card: "rgba(40, 25, 80, 0.10) 0px 2px 25px 0px"
  elevated: "rgba(40, 25, 80, 0.14) 0px 6px 30px 0px"

motion:
  duration-fast: 150ms
  duration-base: 200ms
  duration-slow: 300ms
  easing: "cubic-bezier(0.4, 0, 0.2, 1)"

breakpoints: [480px, 640px, 768px, 1024px, 1200px, 1367px, 1400px, 1728px]
---

## Rationale

Evalio keeps the premium minimalism, compact spacing logic, restrained motion, and editorial typography of the supplied base design, but changes the product meaning from generic technical software into **evidence-first college admissions analysis**.

The deep purple primary (`#281950`) remains because it gives the interface maturity, seriousness, and strong reading contrast. The violet action color is shifted to Evalio Violet (`#6757f5`) and supported by a soft lavender surface (`#f2efff`) so the product has a recognizable analytical identity without becoming a neon AI-style interface.

The design should feel **calm before clever**. Evalio is not trying to look futuristic or magical. It should feel like a trusted analytical publication merged with a precise software product.

The brand is carried less by decoration and more by recurring product language and UI patterns:

> **Every score has a reason.**

and:

```text
Score
→ Evidence
→ Rule
→ Explanation
```

The user should repeatedly encounter scores, confidence, evidence, methodology, and source provenance as visual elements. These are not secondary details; they are the core Evalio identity.

---

## 1. Visual Theme & Atmosphere

Evalio's visual identity is **premium minimalism for admissions analysis**: editorial, analytical, source-aware, and calm.

Preserve the supplied base design's restraint:

- no excessive gradients;
- no neon AI visuals;
- no glassmorphism overload;
- no huge decorative shadows;
- no generic 3D illustrations;
- no unnecessary floating objects.

The interface should rely on:

- typography;
- white space;
- data hierarchy;
- quiet lavender surfaces;
- deep purple text;
- concise status labels;
- structured evidence;
- realistic product UI.

The overall atmosphere is:

> **clarity through evidence**

rather than clarity through emptiness.

White space should remain generous, but important sections should not feel unfinished. Use useful information—scores, confidence badges, source labels, evidence snippets, methodology links, and mini-metrics—to create visual density instead of decorative filler.

---

## 2. Color System

The core palette intentionally stays close to the supplied base.

### Core Colors

- **Primary (`#281950`)** – Evalio Ink. Deep midnight purple used for primary text, structural elements, dark sections, and high-authority typography.
- **On-primary (`#ffffff`)** – Required foreground on dark primary backgrounds.
- **Surface (`#6757f5`)** – Evalio Violet. Primary interactive/action color and selected-state accent.
- **Surface-soft (`#f2efff`)** – Soft lavender used for evidence panels, selected cards, methodology callouts, and subtle section variation.
- **Background (`#ffffff`)** – Main reading canvas.
- **Border (`#d9d3f0`)** – Lavender-neutral border used instead of generic gray.
- **Text (`#281950`)** – Primary copy color.
- **Text-muted (`#686082`)** – Secondary explanation and metadata.
- **Accent (`#6757f5`)** – Links, small highlights, progress lines, focused controls.

### Semantic Colors

- **Success (`#168a5b`)** – Strong, verified, compatible, completed.
- **Warning (`#b7791f`)** – Medium confidence, attention required, incomplete.
- **Danger (`#c24a55`)** – Critical issue, incompatible requirement, severe warning.
- **Confidence High (`#168a5b`)**
- **Confidence Medium (`#b7791f`)**
- **Confidence Low (`#8c6673`)**
- **Verified (`#168a5b`)**

Semantic colors must be used sparingly. Evalio is primarily purple, white, and ink—not a rainbow dashboard.

### Contrast Rule

Never allow important text to inherit an unsafe foreground color.

Required examples:

```text
Evalio Violet button (#6757f5)
→ white text (#ffffff)

White secondary button
→ Evalio Ink text (#281950)

Dark purple section
→ white primary text

Soft lavender card
→ Evalio Ink text
```

A button must never visually disappear into its background.

---

## 3. Typography

Preserve the supplied two-family structure.

### Display & Heading

**Mackinac** with serif fallbacks.

Use for:

- landing-page statements;
- major section headings;
- methodology statements;
- college-evaluation storytelling;
- final CTA headlines.

The serif creates an editorial, academic quality and prevents Evalio from looking like a generic SaaS template.

### Body

**Fricolage Grotesque** with system sans fallbacks.

Use for:

- forms;
- body copy;
- navigation;
- tool labels;
- tables;
- evidence;
- source metadata;
- controls.

### Data Typography

Scores, percentages, labels, and metric rows use the sans-serif stack even when they appear beside a serif headline.

Example:

```text
Know where your
application stands.      ← serif

ACADEMIC STRENGTH        ← sans
91 / 100                 ← sans
HIGH CONFIDENCE          ← sans
```

This creates Evalio's intended split:

> **editorial outside, quantitative inside**

### Eyebrow Labels

Use small uppercase labels as a recurring Evalio signature:

```text
EVALIO / APPLICATION ANALYSIS
EVALIO / ESSAY
EVALIO / COLLEGE DATA
EVALIO / METHODOLOGY
EVALIO / RECOMMENDATION LETTER
```

Eyebrows are:

- 11px;
- semibold;
- uppercase;
- violet;
- letter-spaced;
- short.

Do not overuse them on every card. They belong at section/tool level.

---

## 4. Components & Patterns

### Primary Actions

Primary CTA:

```text
background: #6757f5
text: #ffffff
border: #6757f5
radius: 10px or pill
```

Examples:

```text
Evaluate my application →
Analyze an essay →
Evaluate my profile →
```

Primary text must remain white in default, hover, focus, and active states.

### Secondary Actions

```text
background: #ffffff
text: #281950
border: #d9d3f0
```

Examples:

```text
View methodology
Compare colleges
Privacy details
```

### Ghost Actions

Use only on clean backgrounds:

```text
background: transparent
text: #281950
```

A ghost action on a dark section must switch to an explicitly light foreground variant.

### Navigation & Header

Keep the supplied compact white navigation style.

Suggested public navigation:

```text
Evalio

Tools
Colleges
Methodology

Sign In
Get Started →
```

Evalio logo/wordmark should remain visually compact. Do not make the navbar itself the branding moment.

### Featured Sections

Use either:

```text
white
soft lavender
deep Evalio Ink
Evalio Violet
```

Avoid creating a different arbitrary background color for every section.

### Cards

Cards should be:

- white or soft lavender;
- `10px–16px` radius;
- thin lavender border where separation is needed;
- subtle purple-tinted shadow;
- moderately dense;
- evidence/data-first.

Avoid identical cards everywhere. Some sections should use open layouts without card containers.

### Borders & Dividers

Use `#d9d3f0` for light dividers.

On dark sections use:

```text
rgba(255,255,255,0.14)
```

Do not use pure white borders on white backgrounds.

---

## 5. Evalio Brand Signatures

These patterns make the base design recognizably Evalio.

### 5.1 Every Score Has a Reason

Where practical, scored outputs should provide this path:

```text
Score
→ component
→ evidence
→ rule
→ explanation
```

Example:

```text
ACADEMIC STRENGTH

91 / 100                 HIGH CONFIDENCE

Performance              94
Course rigor             88
Academic trend           90

3 rules contributed

View evidence →
```

### 5.2 Evidence Rail

Evidence should have a recognizable visual treatment:

```text
EVIDENCE

Academic trend
+4.2 points across four terms

RULE
ACAD-003

EFFECT
+6.5 points
```

Recommended styling:

- narrow violet left rail or top rule;
- soft-lavender background;
- small uppercase metadata;
- no giant icon.

### 5.3 Confidence Badge

Confidence is a first-class piece of information.

Examples:

```text
● HIGH CONFIDENCE
● MEDIUM CONFIDENCE
● LOW CONFIDENCE
```

Never communicate confidence using color alone; always show the text label.

### 5.4 Source Provenance

College and scholarship data should visually expose provenance.

Example:

```text
SOURCE STATUS

✓ Verified
2026–27 cycle
Updated Sep 2026
```

or compact:

```text
Verified source · Current cycle
```

Source/freshness UI should use small type and restrained green.

### 5.5 Evalio Score Card

A recurring card pattern:

```text
╭────────────────────────────────╮
│ ACADEMIC STRENGTH      STRONG  │
│                                │
│ 91 / 100      HIGH CONFIDENCE  │
│                                │
│ Performance              94    │
│ Rigor                    88    │
│ Trend                    90    │
│                                │
│ View evidence →                │
╰────────────────────────────────╯
```

Visual rules:

- white or lavender surface;
- lavender border;
- small violet category label;
- score large but not oversized;
- confidence visually secondary to score;
- evidence link always obvious.

### 5.6 Planning Category

College fit should never imitate a probability meter.

Preferred:

```text
PLANNING CATEGORY

HIGH REACH

Why this result? →
```

paired with separate dimensions:

```text
Academic alignment   STRONG
Selectivity risk     VERY HIGH
Requirements fit     COMPATIBLE
Financial fit        STRONG
Data confidence      HIGH
```

### 5.7 Brand Copy

Preferred Evalio language:

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

Avoid generic startup language:

```text
Unlock your potential
Revolutionize your future
Supercharge your application
AI-powered admissions magic
```

---

## 6. Spacing & Layout

Preserve the existing **4px base unit** and spacing scale:

```text
4, 8, 12, 16, 20, 24, 32, 40, 48, 64px
```

Typical patterns:

- component padding: `12–24px`;
- major card padding: `20–32px`;
- column gutters: `16–24px`;
- section spacing: `48–96px` depending on viewport;
- compact mobile spacing: reduce one or two scale steps.

The key Evalio adjustment is **controlled information density**.

Do not solve emptiness by shrinking all white space.

Instead:

```text
white space
+
useful evidence
+
small metadata
+
real product UI
```

Desktop sections may use asymmetry:

```text
large editorial statement        compact data panel
```

or:

```text
product interface                explanation
```

Avoid repeating the same centered heading + 3-card grid pattern in every section.

---

## 7. Motion & Interaction

Preserve the supplied motion system:

- fast: `150ms`;
- base: `200ms`;
- slow: `300ms`;
- easing: `cubic-bezier(0.4, 0, 0.2, 1)`.

Motion remains **restrained and purposeful**.

Preferred:

- button color transition;
- border/focus transition;
- subtle card elevation;
- accordion opening;
- evidence drawer;
- score reveal;
- selected-state movement of 1–2px maximum if needed.

Avoid:

- floating decorative objects;
- looping animations;
- excessive parallax;
- fake progress bars;
- dramatic scroll reveals;
- animated gradient backgrounds.

Evalio should feel fast and predictable.

---

## 8. Accessibility

### Contrast

Core pairs must meet WCAG AA at minimum.

Required:

```text
#281950 on #ffffff
#ffffff on #6757f5
#281950 on #f2efff
#ffffff on #281950
```

Primary and secondary CTA variants must be tested independently.

Never depend on inherited text color for buttons.

### Touch Targets

Interactive elements:

```text
minimum 44×44px
```

where practical, especially on mobile.

### Focus

Use a visible 2px focus outline/ring.

Recommended:

```text
outline/ring: #6757f5
offset: 2px
```

On violet backgrounds use a white or high-contrast alternative.

### Keyboard

All:

- CTAs;
- tabs;
- filters;
- inputs;
- accordions;
- dialogs;
- evidence drawers;
- source links

must be keyboard-accessible.

### Color Independence

Statuses must always include labels.

Good:

```text
● HIGH CONFIDENCE
```

Bad:

```text
●
```

### Motion

Respect:

```text
prefers-reduced-motion
```

---

## 9. Implementation Guardrails for Codex

When implementing this design:

1. Preserve the existing Fly-derived spacing, radius, serif/sans hierarchy, and restrained motion unless a specific Evalio requirement overrides it.
2. Use Evalio Ink (`#281950`) as the dominant structural/text color.
3. Use Evalio Violet (`#6757f5`) as the primary action/accent.
4. Do not introduce unrelated blues, teals, pink gradients, or neon AI colors.
5. Use soft lavender (`#f2efff`) for analytical/evidence surfaces.
6. Use semantic green/amber/red only for status meaning.
7. Primary CTA text must always be white.
8. Secondary CTA text must always be Evalio Ink.
9. Audit hover/focus/active/disabled variants for contrast.
10. Avoid generic "AI-generated SaaS" card grids.
11. Prefer real product data previews over decorative illustrations.
12. Use `Score → Evidence → Rule → Explanation` throughout evaluator surfaces.
13. Show confidence where a score is shown and confidence data exists.
14. Show source/freshness indicators on externally sourced college/scholarship facts.
15. Never display fake admission probability.
16. Never display AI-authorship probability.
17. Keep marketing pages editorial; keep tools quantitative.
18. Keep the page visually calm, but never empty due to missing product detail.

---

## Final Evalio Design Principle

When choosing between:

```text
more decoration
```

and:

```text
clearer evidence
```

choose:

> **clearer evidence**

When choosing between:

```text
a generic SaaS pattern
```

and:

```text
an Evalio-specific analytical pattern
```

choose:

> **the Evalio pattern**

The finished product should feel familiar enough to retain the premium, restrained quality of the provided base design, but unmistakably belong to Evalio through its violet action language, editorial admissions tone, score cards, confidence labels, evidence rails, and source provenance.
