# UI_UX_SPEC.md

# Web UI / UX Specification

**Version:** 1.0.0  
**Design goal:** Clear, serious, evidence-driven, student-friendly

---

## 1. Design Principles

1. Explain before impressing.
2. Scores must always have context.
3. Avoid fake certainty.
4. Mobile is a first-class experience.
5. Sensitive material should feel private.
6. Use progressive disclosure instead of overwhelming users.
7. No dark patterns around account creation.

---

## 2. Visual Direction

Style:

- clean academic/product UI;
- spacious;
- restrained;
- professional;
- not “AI neon”;
- no chatbot-first interface.

Use one neutral base with one primary accent configured through design tokens.

Do not hard-code semantic meaning only to color.

---

## 3. Main Navigation

Desktop:

```text
Logo | Dashboard | Essay | Profile | Colleges | Methodology | Account
```

Anonymous:

```text
Logo | Essay | Activity Analyzer | Colleges | Methodology | Sign In
```

Mobile:

- compact header;
- accessible menu;
- primary CTA visible where relevant.

---

## 4. Landing Page

Sections:

1. Hero
2. Core tools
3. Explainable scoring concept
4. What the system can/cannot judge
5. College-data provenance
6. Privacy
7. CTA

Suggested hero copy concept:

```text
Understand your college application.
Without black-box AI.
```

Do not claim official admissions prediction.

---

## 5. Dashboard

Top:

```text
Profile Strength Index
Application Readiness
Target Colleges
Critical Issues
```

Component cards:

```text
Academics
Activities
Honors
Essay Signals
LOR Signals
Testing
```

Each card:

- score/status;
- short explanation;
- confidence;
- `Why?`;
- `Improve` link.

---

## 6. Score Component

Example:

```text
Academic Strength
91 / 100
Strong

Confidence: High

[ Why this score? ]
```

Expanded:

```text
Performance       94 × 45%
Rigor             88 × 30%
Trend             90 × 10%
Context           85 × 10%
Major Prep        92 × 5%
```

Always show methodology link.

---

## 7. Essay Analyzer

Desktop two-column after analysis:

```text
LEFT
Essay editor/text

RIGHT
Score + components + issues
```

Mobile:

```text
Essay
↓
Analyze
↓
Summary
↓
Components
↓
Priority issues
↓
Sentence-level findings
```

Input:

- paste text;
- optional upload;
- essay type;
- word limit.

Live word count may be client-side because it is presentation-only, but authoritative evaluation comes from API.

---

## 8. Essay Results

Display:

```text
Mechanical Essay Score
```

Never:

```text
Admissions Essay Quality
Authenticity Score
Chance Boost
```

Sections:

1. overall mechanical score;
2. measurable metrics;
3. component scores;
4. top priorities;
5. all triggered rules;
6. methodology;
7. disclaimer.

---

## 9. Rule Issue Card

Example:

```text
Medium
Repeated reflection phrase

"I realized" appears 4 times.

Evidence:
Sentences 8, 15, 22, 31

Effect:
Reflection marker repetition has diminishing value.
```

Do not automatically rewrite the sentence.

---

## 10. Profile Setup

Use wizard only where it reduces complexity.

Suggested:

```text
1. Basics
2. School/Curriculum
3. Academics
4. Testing
5. Activities
6. Honors
7. Review
```

Allow save-and-return for authenticated users.

---

## 11. Academic Input

Support:

- semester averages;
- course-level detail;
- custom grading scale;
- class rank optional;
- school advanced-course availability.

Never force a 4.0 GPA input for international users.

---

## 12. Activity UI

Activity list cards show:

- title;
- organization;
- duration;
- hours;
- current internal score/status.

Editor shows Common App character count where applicable.

Portfolio page visually emphasizes top meaningful activities rather than count.

---

## 13. College Explorer

Search:

- text search;
- country/state;
- test policy;
- financial aid policy;
- application platform;
- optional selectivity bands.

College card should show only decision-useful summary.

Do not overload cards with all database fields.

---

## 14. College Detail

Sections:

```text
Overview
Admissions
Testing
Application Requirements
International Applicants
Financial Aid
Sources & Freshness
```

If logged in:

```text
Evaluate My Profile
```

---

## 15. College Evaluation Result

Never show a pie chart implying probability.

Use separate cards:

```text
Academic Alignment
Selectivity Risk
Requirements Fit
Financial Fit
Data Confidence
Planning Category
```

Then:

```text
Why this category?
```

---

## 16. Application Audit

Checklist rows:

```text
Required / Optional
Complete / Missing
Deadline
Quality status
Action
```

Critical issues at top.

Do not combine completeness and quality into one ambiguous check mark.

---

## 17. Methodology

Public and readable.

Each evaluator has:

- what is measured;
- formula/weights;
- what is not measured;
- limitations;
- current rubric version.

This is a product feature, not just legal text.

---

## 18. Authentication UX

Anonymous tools remain available.

Only ask user to sign in when they want to:

- save profile;
- save analysis;
- build target list;
- generate persistent reports.

Avoid blocking first analysis behind signup.

---

## 19. Privacy UX

Before saving essay/LOR:

```text
Save this text to my account
[ ] unchecked by default
```

Explain:

- analysis can run without saving raw text;
- metrics/results may be saved separately if user chooses.

---

## 20. Errors

Good:

```text
This PDF does not contain extractable text.
Upload a text-based PDF, DOCX, TXT, or paste the text directly.
```

Bad:

```text
500 parser exception
```

Errors should preserve user input in the browser where safe so they do not have to retype.

---

## 21. Loading

Use specific labels:

```text
Analyzing essay…
Checking college requirements…
Calculating academic alignment…
```

Do not use fake progress percentages.

---

## 22. Empty States

Example:

```text
No activities yet.
Add your first activity to build your activity profile.
```

Provide one clear action.

---

## 23. Responsive Rules

At <= 767px:

- single column;
- sticky bottom action only when useful;
- no wide tables without responsive transformation;
- charts become text/cards if unreadable.

At >= 1024px:

- allow two-column analyzer;
- dashboard multi-column cards.

---

## 24. Accessibility

Required:

- semantic `button`, `label`, `input`;
- keyboard complete;
- focus visible;
- ARIA only when semantic HTML is insufficient;
- error summary at top of failed forms;
- inline field errors;
- score status text accompanies color/icon;
- reduced motion honored.

---

## 25. Content Tone

Use:

```text
Strong signal
Limited data
Requirement incomplete
High selectivity
Possible with substantial aid
```

Avoid:

```text
You're definitely getting in
Bad applicant
Weak person
AI says
Guaranteed
```

---

## 26. Design-System Components

Minimum reusable components:

```text
Button
Input
Textarea
Select
Checkbox
RadioGroup
Dialog
Drawer
Tabs
Card
ScoreCard
ConfidenceBadge
StatusBadge
RuleIssue
MetricRow
ProgressBar
DataFreshnessBadge
SourceList
EmptyState
ErrorState
Skeleton
Toast
```

---

## 27. E2E UX Acceptance

A new mobile user must be able to:

```text
land
→ open essay analyzer
→ paste essay
→ analyze
→ understand the score
→ expand why
```

without creating an account.

An authenticated user must be able to:

```text
dashboard
→ update profile
→ evaluate college
→ audit application
→ understand all result reasons
```

without needing Discord or another external interface.
