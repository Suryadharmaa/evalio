# PRD.md

# Deterministic College Admissions Evaluation Engine
## Product Requirements Document — Web Edition

**Version:** 2.0.0  
**Primary surface:** Responsive web application  
**Deployment target:** Vercel  
**Frontend:** Next.js + React + TypeScript  
**Backend:** Python API on Vercel Functions  
**Database/Auth:** Supabase PostgreSQL + Supabase Auth  
**AI/LLM/ML:** None  
**Primary market:** US undergraduate admissions, including international applicants

---

## 1. Product Summary

Build a transparent college-admissions evaluation platform that analyzes measurable application signals without using LLMs, machine learning, embeddings, vector databases, or generative AI.

The product evaluates:

- academic performance;
- academic trend;
- course rigor;
- standardized testing;
- extracurricular activities;
- activity descriptions;
- honors and awards;
- Common App personal statements;
- supplemental essays;
- recommendation-letter signals;
- college academic alignment;
- application requirements;
- financial fit;
- application completeness;
- overall application readiness.

Every score must be explainable from:

```text
user input
+ deterministic rule
+ published rubric
+ versioned college data
= result
```

The system must never present an internal score as an official university score or guaranteed admission probability.

---

## 2. Product Positioning

Preferred positioning:

> Explainable College Admissions Evaluation Engine

Core differentiators:

- no AI hallucination;
- no LLM or AI API cost;
- deterministic results;
- explainable scoring;
- privacy-conscious processing;
- college-specific source provenance;
- international curriculum support;
- measurable essay feedback;
- reproducible results across versions.

Do not market the product as an AI admissions officer.

---

## 3. User Types

### 3.1 Anonymous Visitor

Can:

- analyze an essay;
- analyze an activity description;
- browse public college data;
- view methodology.

Anonymous analyses are not saved by default.

### 3.2 Authenticated Applicant

Can additionally:

- create applicant profile;
- save academics/tests/activities/honors;
- save target college list;
- run college evaluations;
- run application audits;
- save reports;
- export/delete account data.

### 3.3 Admin

Can:

- import college datasets;
- validate staging data;
- approve data promotion;
- inspect stale sources;
- manage rule/data versions;
- review system health.

Admin cannot read user essays or recommendation text unless explicit debugging consent is implemented in a future version.

---

## 4. Primary User Journeys

### Journey A — Essay analysis

```text
Landing page
→ Essay Analyzer
→ Paste text / upload supported document
→ Select essay type and word limit
→ Analyze
→ Mechanical Essay Score
→ component scores
→ triggered rules
→ evidence
→ priorities
```

### Journey B — Build applicant profile

```text
Sign in
→ Dashboard
→ Profile setup
→ Academics
→ Testing
→ Activities
→ Honors
→ Profile Strength
```

### Journey C — Evaluate college

```text
College Explorer
→ Select college
→ Compare against saved profile
→ Academic Alignment
→ Selectivity Risk
→ Requirements Fit
→ Financial Fit
→ Data Confidence
→ Planning Category
→ Why this result?
```

### Journey D — Application audit

```text
Target College
→ Application Audit
→ Required materials
→ Missing materials
→ deadline status
→ quality/readiness status
→ prioritized actions
```

---

## 5. Required Pages

Public:

```text
/
 /essay
 /activity-analyzer
 /colleges
 /colleges/[slug]
 /methodology
 /privacy
 /terms
```

Authenticated:

```text
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

Admin:

```text
/admin
/admin/imports
/admin/colleges
/admin/sources
/admin/rules
/admin/system
```

---

## 6. Core Evaluation Modules

### 6.1 Academic Engine

Outputs:

- Academic Performance;
- Academic Trend;
- Course Rigor;
- Academic Context;
- Major Preparation;
- Academic Strength.

No forced conversion from Indonesian percentages, IB, A-Level, or other systems into US 4.0 GPA.

### 6.2 Activity Engine

Outputs:

- individual activity score;
- portfolio score;
- leadership/responsibility;
- impact;
- initiative;
- duration;
- recognition;
- progression;
- description quality indicators.

More activities must not automatically increase score.

### 6.3 Honors Engine

Evaluates:

- scope;
- selectivity;
- placement;
- recurrence;
- academic relevance.

Award title alone must never determine prestige.

### 6.4 Essay Engine

Outputs a **Mechanical Essay Score**, not a semantic judgment.

Measures:

- compliance;
- readability/clarity;
- structure;
- specificity signals;
- reflection signals;
- voice indicators;
- sentence variety;
- repetition/style hygiene.

The engine must not claim to understand:

- true authenticity;
- emotional depth;
- personality;
- admissions-officer reaction.

### 6.5 Recommendation-Letter Engine

Outputs deterministic signals for:

- relationship context;
- specific evidence;
- academic traits;
- community traits;
- comparative evidence;
- generic-praise risk.

### 6.6 College Engine

Returns separately:

- Academic Alignment;
- Application Strength;
- Requirements Fit;
- Financial Fit;
- Selectivity Risk;
- Data Confidence;
- Planning Category.

Never collapse these into a fake exact acceptance probability.

---

## 7. Planning Categories

Allowed:

```text
HIGH_REACH
REACH
COMPETITIVE
LIKELY_ISH
INSUFFICIENT_DATA
```

Never display:

```text
GUARANTEED
SAFETY
100% CHANCE
```

for selective holistic admissions.

---

## 8. College Data Requirements

Each critical college fact must include:

```text
value
academic_cycle
source_type
source_url
retrieved_at
verified_at
freshness
confidence
```

Preferred source priority:

1. official admissions site;
2. official financial-aid site;
3. Common Data Set;
4. IPEDS;
5. College Scorecard;
6. Common App;
7. manually verified official source.

Critical cycle-sensitive data:

- deadlines;
- test policy;
- essay requirements;
- recommendation requirements;
- English-proficiency policy;
- financial-aid policy;
- tuition/cost of attendance.

---

## 9. Authentication

Use Supabase Auth.

Initial supported methods:

- email + password;
- email magic link/OTP.

Social login is optional after MVP.

Public analyzers should remain usable without account.

Protected API requests must use verified access tokens.

---

## 10. Persistence Rules

Anonymous:

- do not persist raw essay/LOR;
- do not persist profile data;
- temporary upload discarded after request;
- rate-limit metadata may be stored using privacy-preserving identifiers.

Authenticated:

- structured applicant data may persist;
- raw essay/LOR text persists only if user explicitly chooses Save;
- evaluation metrics/results may persist;
- user can export/delete data.

---

## 11. File Support

Supported:

- TXT;
- Markdown;
- DOCX;
- text-based PDF;
- CSV for structured academics.

No OCR in V1.

Image-only/scanned PDFs must return a clear unsupported-text response.

Because Vercel Functions have a bounded request/response payload, the product-level direct upload limit is **4 MB** per request. Larger-document support is out of scope for V1.

---

## 12. Dashboard Requirements

Dashboard shows:

- Profile Strength Index;
- Academics;
- Activities;
- Honors;
- Essay Signals;
- LOR Signals;
- target colleges;
- critical application issues;
- application readiness;
- data-quality warnings.

Every score card must expose a `Why?` or equivalent detail view.

---

## 13. Methodology Requirements

Public methodology pages must explain:

- score definitions;
- component weights;
- deterministic limitations;
- college data provenance;
- confidence;
- versioning;
- why the product does not provide guaranteed admission probabilities.

---

## 14. Responsive UX

Required viewports:

```text
mobile: 360px+
tablet: 768px+
desktop: 1024px+
large desktop: 1440px+
```

Core analysis workflows must be fully usable on mobile.

No essential information may depend on hover.

---

## 15. Accessibility

Target WCAG 2.2 AA practices.

Required:

- keyboard navigation;
- visible focus states;
- semantic headings;
- form labels;
- accessible error text;
- sufficient contrast;
- reduced-motion support;
- score status not communicated by color alone.

---

## 16. Privacy Requirements

The product should not request unnecessary:

- passport data;
- national ID;
- exact home address;
- bank-account information;
- medical information;
- protected demographic attributes.

No numerical admissions boost/penalty may be assigned to protected characteristics.

---

## 17. Non-Goals for V1

Do not build:

- generative essay rewriting;
- AI detector;
- chatbot;
- exact acceptance probability;
- automatic college-site scraping agents;
- OCR;
- scholarship auto-application;
- payment system;
- counselor multi-tenant portal;
- mobile native app.

---

## 18. Success Metrics

Quality:

```text
deterministic reproducibility = 100%
critical rule boundary test coverage = 100%
critical college data source coverage > 95%
critical requirement accuracy target > 99%
```

Product:

- completed essay analyses;
- completed profiles;
- target-college evaluations;
- audit completion;
- repeat usage;
- methodology-detail usage.

---

## 19. Definition of MVP Done

MVP is complete when:

- responsive web app deploys on Vercel;
- anonymous essay analyzer works;
- authenticated profile works;
- academic/activity/honor evaluators work;
- college DB and source provenance work;
- college evaluation works;
- application audit works;
- reports render;
- export/delete-my-data work;
- no AI/LLM/ML dependency exists;
- all critical tests pass.
