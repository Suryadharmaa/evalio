# UI_UX.md

# Evalio — UI / UX Specification
**Version:** 1.0  
**Product:** Deterministic College Admissions Evaluation Platform  
**Design direction:** Editorial SaaS + data-first admissions product  
**Reference inspiration:** Test Ninjas-style clarity and product-first storytelling, with a distinct Evalio identity

---

## 1. Brand Personality

Evalio should feel:

- analytical
- transparent
- calm
- credible
- modern
- student-friendly
- precise, not intimidating

Avoid:

- “AI startup” neon visuals
- glassmorphism overload
- fake certainty
- overly corporate school-software styling
- cluttered dashboards
- playful/cartoonish admissions visuals

Core brand principle:

> **Every score has a reason.**

Supporting message:

> Transparent admissions analysis, without black-box AI.

---

## 2. Visual Direction

### Style

Use:

- large editorial headlines
- short supporting copy
- generous whitespace
- product UI as the main visual
- simple cards
- restrained borders/shadows
- clear numeric hierarchy
- clean sections with strong rhythm

Do not use decorative illustrations when real product UI can explain the feature better.

---

## 3. Evalio Identity

Evalio should not look like a Test Ninjas clone.

Distinctive traits:

- calmer visual tone
- more analytical/data-oriented
- stronger methodology visibility
- “why this score?” interactions everywhere
- confidence + source freshness as first-class UI
- less aggressive admissions marketing
- no exact acceptance-percentage graphics

Signature Evalio pattern:

```text
Score
↓
Evidence
↓
Rule
↓
Explanation
```

---

## 4. Typography

Use a clean modern sans-serif.

Recommended hierarchy:

```text
Hero H1        56–72px desktop / 40–48px mobile
Section H2     40–52px desktop / 30–36px mobile
Card title     22–28px
Body           16–18px
Metadata       13–14px
Microcopy      12–13px
```

Headlines:

- short
- bold
- tight line-height
- usually 2–3 lines maximum

Example:

> Know where your  
> application stands.

Avoid long descriptive headings.

---

## 5. Color System

Use a neutral foundation plus one Evalio accent.

Suggested token structure:

```text
background          warm/light neutral
surface             white / near-white
text-primary        near-black
text-secondary      muted gray
border              soft neutral
primary             Evalio accent
success             muted green
warning             muted amber
danger              muted red
info                 muted blue
```

Rules:

- use color sparingly
- do not communicate score meaning using color alone
- avoid rainbow dashboards
- no neon gradients

---

## 6. Layout

Global content width:

```text
1200–1280px max
```

Section rhythm:

```text
Hero
↓
Trust / principles
↓
Core tools
↓
Product preview
↓
Methodology
↓
College evaluation preview
↓
How it works
↓
Final CTA
```

Each section should communicate one main idea.

Desktop:

- frequent 2-column layouts
- 3–4 card grids

Mobile:

- single-column
- clear vertical hierarchy
- no horizontal overflow

---

## 7. Navigation

### Public

```text
Evalio

Tools
Colleges
Methodology

Sign In
Get Started →
```

### Logged In

```text
Evalio

Dashboard
Profile
Essay
Colleges
Applications

Account
```

Keep navigation compact.

Primary CTA should be visually stronger than secondary navigation.

---

## 8. Landing Page

### Hero

Left:

```text
Know where your
application stands.

Transparent analysis across academics,
activities, essays, and college fit.

[ Evaluate my application → ]
[ Analyze an essay ]
```

Right:

show a realistic Evalio product preview.

Example:

```text
Application Strength
84 / 100

Academics      91   Strong
Activities     84   Strong
Essay          81   Strong
Honors         76   Competitive

Data Confidence
HIGH

3 priority improvements
```

Do not use generic student stock imagery.

---

## 9. Trust Strip

Immediately below hero.

Use product principles, not fake social proof.

Example:

```text
100%
Explainable scoring

0
AI models required

Every
College fact sourced

Versioned
Admissions methodology
```

Only show real statistics.

---

## 10. Core Tools Section

Headline:

> Everything you need  
> to evaluate your application.

Cards:

```text
Academics
Activities
Essay
Honors
College Fit
Application Audit
```

Card format:

```text
small label/icon
large title
1–2 lines description
→ action
```

Minimal shadows.

---

## 11. Dashboard

Top area:

```text
Application Strength      84 / 100
Application Readiness     82%
Data Confidence           HIGH
Critical Issues           2
```

Below:

```text
Academics
Activities
Honors
Essay Signals
LOR Signals
Testing
```

Each score card must include:

```text
score
label
confidence
short explanation
Why? →
```

---

## 12. Score Cards

Example:

```text
ACADEMICS

91
Strong

Performance, rigor, academic trend,
and major preparation.

Confidence: High

Why this score? →
```

Expanded view:

```text
Performance        94 × 45%
Rigor              88 × 30%
Trend              90 × 10%
Context            85 × 10%
Major Prep         92 × 5%
```

---

## 13. Essay Analyzer

Tool pages should be simpler than marketing pages.

### Desktop

```text
LEFT
Essay editor

RIGHT
Evaluation result
```

### Mobile

```text
Essay input
↓
Analyze
↓
Overall score
↓
Components
↓
Priority issues
↓
Sentence findings
```

Input area:

```text
Personal Statement

[ Essay text area ]

628 / 650 words

[ Analyze Essay → ]
```

---

## 14. Essay Results

Always label:

> Mechanical Essay Score

Never:

- Authenticity Score
- Emotional Depth Score
- Admission Boost
- AI Score

Example:

```text
81 / 100
Strong

Clarity              84
Structure            81
Specificity          76
Reflection Signals   83
Voice Indicators     79
Style Hygiene        72
```

---

## 15. Rule / Issue Cards

Example:

```text
MEDIUM

Repeated reflection phrase

“I realized” appears 4 times.

Evidence
Sentences 8, 15, 22, 31

Effect
Repeated markers have diminishing value.

View methodology →
```

Do not automatically rewrite the user's essay.

---

## 16. College Explorer

Search-first interface.

Top:

```text
Explore colleges.

[ Search a college...                  ]
```

Optional filters:

```text
State
Test Policy
Aid Policy
Selectivity
```

College cards should remain simple.

---

## 17. College Detail

Sections:

```text
Overview
Admissions
Testing
Requirements
Financial Aid
International
Sources
```

If logged in:

```text
[ Evaluate My Profile → ]
```

Show source freshness visibly.

---

## 18. College Evaluation

Never use a probability pie chart.

Use separate dimensions:

```text
Academic Alignment     STRONG
Selectivity Risk       VERY HIGH
Requirements Fit       COMPATIBLE
Financial Fit          STRONG
Data Confidence        HIGH

Planning Category
HIGH REACH
```

CTA:

```text
Why this result? →
```

---

## 19. Methodology UI

Methodology should feel like a product feature.

Example:

```text
Academic Strength

Performance       45%
Course Rigor      30%
Academic Trend    10%
Context           10%
Major Prep         5%

[ View rules ]
```

User should always be able to trace:

```text
result
→ component
→ rule
→ evidence
```

---

## 20. Application Audit

Use checklist rows:

```text
Supplemental Essay
Required
Missing
Deadline: Jan 3

Teacher Recommendation
Required
Complete
```

Separate:

```text
Completeness
Quality
```

Never merge both into one ambiguous status.

---

## 21. Authentication UX

Do not force account creation before first analysis.

Anonymous users can:

- analyze essay
- analyze activity description
- browse colleges
- read methodology

Ask for sign-in only when saving:

- profile
- essays
- target colleges
- reports
- application progress

---

## 22. Privacy UX

Saving raw essay/LOR text must be explicit.

Example:

```text
[ ] Save this text to my Evalio account
```

Unchecked by default.

Explain:

> You can analyze your text without saving it.

---

## 23. Buttons

Primary:

```text
Evaluate My Application →
Analyze Essay →
Evaluate My Profile →
```

Secondary:

```text
View Methodology
Learn More
Compare Colleges
```

Avoid excessive CTA variety.

---

## 24. Cards

Evalio cards should be:

- flat or subtle shadow
- soft border
- moderate radius
- clean internal spacing
- data-first

Avoid:

- 3D floating cards
- huge shadows
- glowing borders
- decorative gradients

---

## 25. Motion

Use subtle motion only:

- hover state
- score reveal
- accordion expansion
- soft page transitions
- skeleton loading

Avoid:

- parallax overload
- constant floating animations
- fake loading progress

Respect reduced-motion settings.

---

## 26. Loading States

Use real descriptive states:

```text
Analyzing essay…
Calculating academic strength…
Checking college requirements…
```

Never show fake percentages.

---

## 27. Error States

Good:

```text
This PDF does not contain extractable text.

Upload a text-based PDF, DOCX, TXT,
or paste the text directly.
```

Bad:

```text
Error 500
Parser failed
```

---

## 28. Accessibility

Target WCAG 2.2 AA.

Required:

- keyboard navigation
- visible focus states
- semantic HTML
- form labels
- accessible validation errors
- adequate contrast
- reduced motion
- score meanings shown as text, not color only

---

## 29. Mobile Rules

Minimum width:

```text
360px
```

Mobile:

- single column
- no essential hover interactions
- score tables become stacked rows
- primary actions remain obvious
- avoid fixed-width charts
- no horizontal scrolling

---

## 30. Footer

Keep compact.

```text
Product
Essay Analyzer
Application Evaluation
College Explorer

Methodology
Scoring
Data Sources

Company
Privacy
Terms

© Evalio
```

Do not create a huge SEO directory in V1.

---

## 31. Copy Style

Use:

```text
Strong signal
High confidence
Requirement incomplete
Very high selectivity
Possible with substantial aid
```

Avoid:

```text
You're definitely getting in
Guaranteed
Perfect applicant
AI thinks
72% chance
```

---

## 32. Reusable Components

Minimum:

```text
Button
Input
Textarea
Select
Checkbox
Tabs
Card
ScoreCard
MetricRow
StatusBadge
ConfidenceBadge
RuleIssue
SourceList
FreshnessBadge
ProgressBar
Dialog
Drawer
Skeleton
EmptyState
ErrorState
Toast
```

---

## 33. Evalio Design DNA

```text
EDITORIAL OUTSIDE
+
QUANTITATIVE INSIDE
+
TRANSPARENT EVERYWHERE
```

Marketing pages:

```text
big typography
short copy
product previews
whitespace
```

Tool pages:

```text
minimal
focused
data-first
explainable
```

Evalio should feel inspired by modern admissions SaaS, but distinctly more transparent, analytical, and evidence-driven.

---

## 34. Final Rule

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
