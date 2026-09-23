# TOOLS_SPEC.md

# Evalio Tools Product & Implementation Specification
**Version:** 1.0.0  
**Product:** Evalio — Deterministic College Admissions Evaluation Platform  
**Audience:** Codex / software engineering implementation agent  
**Status:** Authoritative for tool surfaces, flows, routes, and tool-specific integration  
**Last updated:** 2026-09-13

---

# 0. PURPOSE

This document defines the complete implementation plan for Evalio's public and authenticated tool ecosystem.

It translates selected interaction patterns from Test Ninjas into a distinct Evalio experience while preserving Evalio's core product identity:

> **Transparent, deterministic admissions analysis with evidence behind every score.**

The goal is NOT to clone Test Ninjas. The goal is to use proven interaction patterns such as short editorial headings, tool-first pages, large focused inputs, immediate measurable outputs, product previews, strong visual hierarchy, “how it works” explanations, related-tools discovery, and simple data-first result cards.

Evalio must remain visually and functionally distinct.

---

# 1. DOCUMENT PRECEDENCE

Before implementing any tool, read:

1. `docs/PRD.md`
2. `docs/TECHNICAL_DESIGN.md`
3. `docs/DATA_SPEC.md`
4. `docs/SCORING_SPEC.md`
5. `docs/RULEBOOK.md`
6. `docs/API_SPEC.md`
7. `docs/UI_UX.md` or `docs/UI_UX_SPEC.md`
8. `docs/SECURITY.md`
9. `docs/TEST_PLAN.md`
10. `docs/MILESTONE_PLAN.md`
11. **this file: `docs/TOOLS_SPEC.md`**

Conflict rules:

- `SCORING_SPEC.md` and `RULEBOOK.md` remain authoritative for scoring formulas and rule thresholds.
- `DATA_SPEC.md` remains authoritative for normalized database semantics.
- `SECURITY.md` remains authoritative for privacy/security.
- This document is authoritative for tool names, routes, UX flows, tool-specific input/output, API needs, database additions, and reference-inspired interaction patterns.
- If this file conflicts with an older Discord-era requirement, this file wins for the web product.
- If ambiguity remains, report it before inventing behavior.

---

# 2. HARD CONSTRAINTS

Evalio production runtime MUST NOT use:

```text
LLMs
AI APIs
local AI models
machine learning
embeddings
vector databases
OpenAI API
Anthropic API
Gemini API
Ollama
Transformers
PyTorch
TensorFlow
LangChain
LlamaIndex
```

Codex may be used to write code, but the final product runtime must remain deterministic.

Core invariant:

```text
same input
+ same college data snapshot
+ same rule version
+ same engine version
=
same result
```

Do not introduce nondeterministic scoring.

---

# 3. EXTERNAL DESIGN REFERENCES

These URLs are design/interaction references only.

Do NOT copy proprietary copy, logos, illustrations, exact page markup, private datasets, branded assets, or copyrighted screenshots. Use only high-level interaction concepts and create original Evalio components.

## Essay References

### Essay Editor
Reference: `https://test-ninjas.com/college-essay-editor`  
Evalio equivalent: `/tools/essay-evaluator`

Borrow conceptually:
- focused essay textarea;
- optional prompt;
- word counter;
- one primary scoring CTA;
- result dimensions;
- “how it works” section.

Do not copy Test Ninjas scoring dimensions when they conflict with Evalio's existing rubric.

### AI Essay Detector
Reference: `https://test-ninjas.com/ai-essay-detector`  
Evalio equivalent: `/tools/writing-pattern-checker`

Borrow conceptually:
- many measurable writing signals;
- grouped signal output;
- explanations of detected patterns.

Do NOT output a fake AI probability. Evalio must explicitly state:

> This tool detects measurable writing patterns. It cannot determine who or what wrote a text.

### Essay Idea Generator
Reference: `https://test-ninjas.com/college-essay-idea-generator`  
Evalio equivalent: `/tools/essay-idea-builder`

Borrow conceptually:
- guided brainstorming;
- structured prompts;
- experience/value/story inputs;
- multiple idea directions.

Do NOT generate a polished essay with a language model.

## Application References

### Admissions Chances
Reference: `https://test-ninjas.com/college-admissions-chances`  
Evalio equivalent: `/tools/application-evaluator`

Borrow conceptually:
- one target college;
- applicant profile inputs;
- centralized evaluation result;
- college-specific result.

Do NOT output exact acceptance probability.

### GPA Calculators
Reference: `https://test-ninjas.com/gpa-calculators`  
Evalio equivalent: `/tools/gpa`

Borrow conceptually:
- dynamic course rows;
- weighted/unweighted modes;
- immediate calculation;
- clear numeric output.

Evalio must additionally support international grading systems without forcing a 4.0 conversion.

### College Profiles
Reference: `https://test-ninjas.com/college-profiles`  
Evalio equivalent: `/colleges`

Borrow conceptually:
- search-first discovery;
- visual school cards;
- college detail pages;
- recognizable institution imagery.

Do NOT claim access to applicant-outcome profiles unless Evalio actually has a verified dataset for them.

### Coursework Evaluator
Reference: `https://test-ninjas.com/college-coursework-evaluator`  
Evalio equivalent: `/tools/coursework-evaluator`

Borrow conceptually:
- course-rigor input;
- school-opportunity context;
- intended-major context;
- rigor result.

Evalio must explicitly avoid penalizing students for unavailable AP/IB/Honors offerings.

### Scholarship Tracker
Reference: `https://test-ninjas.com/college-scholarship-tracker`  
Evalio equivalent: `/tools/scholarships`

Borrow conceptually:
- scholarship directory;
- filters;
- deadline;
- award amount/type;
- tracking state;
- saved list.

Evalio should emphasize international eligibility.

## Recommendation Letter References

### LOR Writer
Reference: `https://test-ninjas.com/college-lor-writer`  
Evalio equivalent: `/tools/lor-builder`

Borrow conceptually:
- structured recommender/student inputs;
- relationship context;
- specific examples;
- guided output.

Because Evalio has no LLM, output a deterministic recommendation-letter framework/template rather than an AI-authored finished letter.

### LOR Evaluator
Reference: `https://test-ninjas.com/college-lor-evaluator`  
Evalio equivalent: `/tools/lor-evaluator`

Borrow conceptually:
- paste full letter;
- score dimensions;
- identify specificity;
- detect generic praise;
- detect comparative language;
- surface evidence.

Use Evalio's deterministic LOR rules only.

---

# 4. EVALIO DESIGN DNA

Evalio should feel like:

```text
editorial outside
+
quantitative inside
+
transparent everywhere
```

Marketing/tool-intro surfaces:
- large, short headlines;
- generous whitespace;
- concise copy;
- real product UI;
- one dominant CTA;
- minimal visual noise.

Tool surfaces:
- focused;
- data-first;
- evidence-first;
- clear inputs;
- deterministic results;
- strong `Why?` affordances.

Distinctive Evalio result flow:

```text
Score
↓
Evidence
↓
Rule
↓
Explanation
```

Never hide scoring logic behind “AI says”, “proprietary intelligence”, or black-box assessment language.

---

# 5. GLOBAL TOOL PAGE TEMPLATE

Every Evalio tool should use the same skeleton unless a tool genuinely needs another interaction model.

```text
← Tools

TOOL NAME.

One short sentence explaining exactly what the tool does.

[ PRIMARY INPUT AREA ]

[ PRIMARY ACTION → ]

------------------------------

RESULT

------------------------------

How it works

01 Input
02 Analyze / Calculate
03 Understand / Act

------------------------------

Methodology

See how this is calculated →

------------------------------

Related tools

[ Tool ] [ Tool ] [ Tool ]
```

---

# 6. TOOLS NAVIGATION

Public navigation:

```text
Evalio

Tools ▾
Colleges
Methodology

Sign In
Get Started →
```

Tools dropdown:

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

`College Explorer` remains a top-level product surface under `/colleges`.

---

# 7. TOOL 1 — ESSAY EVALUATOR

Route: `/tools/essay-evaluator`

API:
```text
POST /api/v1/evaluations/essay
POST /api/v1/evaluations/essay/upload
```

## Goal
Provide deterministic, explainable analysis of measurable essay characteristics. This is not semantic admissions prediction, an authenticity detector, or an AI-generated-text detector.

## Inputs
Required:
```text
essay_text
essay_type
```

Optional:
```text
prompt_text
min_words
word_limit
title
save_raw_text
```

Supported types:
```text
COMMON_APP
SUPPLEMENTAL
SCHOLARSHIP
OTHER
```

File support:
```text
TXT
MD
DOCX
text-based PDF
```

No OCR.

## Primary UI
```text
College Essay Evaluator.

Get transparent feedback on the measurable
strengths and weaknesses of your essay.

+ Add essay prompt

┌──────────────────────────────────────────┐
│ Paste your essay here...                 │
│                                          │
│                                          │
└──────────────────────────────────────────┘

628 / 650 words

[ Analyze Essay → ]
```

Desktop result layout:
```text
LEFT
essay text/editor

RIGHT
score
components
priority findings
```

Mobile:
```text
input
↓
CTA
↓
overall result
↓
components
↓
priority findings
↓
line/sentence evidence
```

## Result
Label:
```text
Mechanical Essay Score
```

Never:
```text
Authenticity Score
Admissions Probability
AI Score
Emotional Depth Score
```

Required dimensions:
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

Example:
```text
MECHANICAL ESSAY SCORE

81 / 100
Strong

Compliance             100
Clarity                  84
Structure                81
Specificity              76
Reflection Signals       83
Voice Indicators         79
Sentence Variety         86
Style Hygiene            72
```

## Findings
Every finding must contain:
```text
rule_id
severity
title
message
evidence
score_effect
confidence
methodology_link
```

Example:
```text
MEDIUM

Repeated reflection phrase

“I realized” appears 4 times.

Evidence
Sentences 8, 15, 22, 31

Rule
ESSAY-014

Effect
Diminishing value after repeated use.

Why this matters →
```

## Persistence
Anonymous: analyze but do not save raw text.  
Authenticated: save raw essay text only if explicit opt-in.

## Acceptance Criteria
- deterministic result;
- no AI dependency;
- word count visible;
- result dimensions match scoring spec;
- every triggered rule exposes evidence;
- anonymous user can complete analysis;
- raw text not persisted by default;
- mobile usable at 360px width.

---

# 8. TOOL 2 — WRITING PATTERN CHECKER

Route: `/tools/writing-pattern-checker`

Suggested API:
```text
POST /api/v1/evaluations/writing-patterns
```

## Goal
Identify deterministic writing-pattern signals commonly associated with overly formulaic, repetitive, generic, or machine-like prose.

The tool MUST NOT claim to identify AI authorship.

Mandatory disclaimer:

> This tool identifies measurable writing patterns. It cannot determine who or what wrote a text.

## Candidate Signals
Implement only deterministic metrics:

```text
sentence_length_uniformity
paragraph_length_uniformity
lexical_diversity
repeated_ngram_rate
transition_phrase_overuse
cliche_density
abstract_language_density
specific_detail_density
named_detail_density
numeric_detail_density
first_person_consistency
contraction_usage
punctuation_diversity
sentence_opening_repetition
reflection_marker_repetition
vocabulary_sophistication
over_formality
filler_phrase_density
hedging_density
passive_construction_proxy
sensory_language_density
pronoun_distribution
sentence_type_variety
short_sentence_frequency
long_sentence_frequency
```

Do not invent a probabilistic classifier.

## Result
Use:
```text
WRITING PATTERN RISK
LOW | MODERATE | HIGH
```

Example:
```text
MODERATE

7 / 24 signals triggered

Rhythm uniformity          HIGH
Specific-detail density    LOW
Repeated transitions       MEDIUM
Vocabulary variation       NORMAL
Sentence variety           STRONG
```

Every triggered signal must show metric, observed value, threshold, sentence/paragraph evidence where applicable, and explanation.

## Acceptance Criteria
- no AI probability;
- no human/AI binary;
- no ML packages;
- all signals reproducible;
- disclaimer visible;
- evidence shown for each triggered pattern.

---

# 9. TOOL 3 — ESSAY IDEA BUILDER

Route: `/tools/essay-idea-builder`

Suggested API:
```text
POST /api/v1/essay-ideas/build
```

May be server-side or client-side if deterministic.

## Goal
Help students identify promising story directions without writing the essay for them.

## Inputs
```text
essay_type
prompt_selection
experiences[]
activities[]
values[]
challenges[]
turning_points[]
specific_moments[]
people_or_places[]
lessons_or_changes[]
```

Suggested value dictionary:
```text
curiosity
responsibility
independence
resilience
leadership
service
creativity
community
family
discipline
risk
identity
learning
adaptability
```

## Deterministic Idea Construction
```text
specific moment
+
tension/challenge
+
value
+
change
+
reflection direction
```

Do not produce a polished essay draft.

## Output
Generate 3–8 structured directions.

Example:
```text
IDEA 01

The 3 AM server outage

Moment
A critical customer outage during your hosting project.

Tension
Responsibility vs. being unprepared.

Core value
Ownership.

Change
You stopped viewing leadership as control and began
viewing it as responsibility under uncertainty.

Possible fit
Common App Prompt 5

Questions to explore
- What exactly happened that night?
- What did you believe before the incident?
- What changed after?
```

## Acceptance Criteria
- ideas are structurally generated;
- no LLM;
- no complete essay drafting;
- outputs are clearly brainstorming prompts;
- editing inputs changes output deterministically.

---

# 10. TOOL 4 — APPLICATION EVALUATOR

Route: `/tools/application-evaluator`

API:
```text
POST /api/v1/profiles/{profile_id}/colleges/{college_id}/evaluate
```

## Goal
Evaluate an applicant against a specific college using separate dimensions rather than fake admission probability.

## Inputs
Preferred authenticated flow:
```text
saved_profile
target_college
evaluation_date
```

Evaluation uses existing academics, testing, activities, honors, essay result, LOR result, college data, financial profile, and requirements.

## Output
Required:
```text
Application Strength
Academic Alignment
Course Rigor
Activities
Honors
Testing
Selectivity Risk
Requirements Fit
Financial Fit
Data Confidence
Planning Category
```

Example:
```text
BOWDOIN COLLEGE

Application Strength       84
Academic Alignment         88
Course Rigor               91
Activities                 84
Honors                     76
Testing                    N/A

Selectivity Risk
VERY HIGH

Requirements
COMPATIBLE

Financial Fit
STRONG

Data Confidence
HIGH

PLANNING CATEGORY
HIGH REACH
```

Never display exact admission chance, likely admitted, guaranteed, or safety labels for selective holistic institutions.

## Why Result
Every planning category must have a traceable explanation.

## Acceptance Criteria
- no probability;
- dimensions remain separate;
- category follows scoring spec;
- data confidence visible;
- college-data cycle visible;
- source freshness visible.

---

# 11. TOOL 5 — GPA TOOLKIT

Route: `/tools/gpa`

Suggested API:
```text
POST /api/v1/calculators/gpa
```

May calculate client-side for immediate UX only if saved/authoritative calculations use the exact documented method.

## Modes
```text
High School GPA
Weighted GPA
Unweighted GPA
Cumulative GPA
Percentage
International
```

## US Course Input
Rows:
```text
Course
Grade
Course Level
Credits
```

Course levels:
```text
REGULAR
HONORS
AP
IB
DUAL_ENROLLMENT
OTHER_ADVANCED
```

Do not assume one universal weighted-GPA scale. Require a selected/documented weighting method.

## International Mode
Support custom percentage scale, semester averages, term averages, course grades, and curriculum name.

Mandatory principle:

> Evalio does not force international grades into a 4.0 GPA unless the user explicitly selects a documented conversion method.

Example result:
```text
Academic Average
90.53 / 100

Scale
0–100

Conversion
Not applied
```

## Acceptance Criteria
- US weighted/unweighted supported;
- international raw-scale mode supported;
- no hidden 4.0 conversion;
- methodology visible;
- exact formula shown.

---

# 12. TOOL 6 — COLLEGE EXPLORER

Routes:
```text
/colleges
/colleges/[slug]
```

API:
```text
GET /api/v1/colleges
GET /api/v1/colleges/{slug}
```

## Goal
Provide source-backed college discovery and detailed institution profiles.

## Search
```text
Explore colleges.

[ Search Harvard, Bowdoin, Stanford...        ]
```

Filters:
```text
country
state
test_policy
need_policy
application_platform
institution_type
selectivity_band
```

Default:
```text
country = US
state = ALL
```

Search debounce: `300ms`.

## College Card
Show useful summary only:
```text
campus image
college name
city, state
institution type
test policy
aid policy
```

## College Detail Sections
```text
Overview
Admissions
Testing
Application Requirements
International Applicants
Financial Aid
Costs
Sources & Freshness
```

Authenticated CTA:
```text
Evaluate My Profile →
```

## Real Campus Images
Add/maintain `college_media` with:
```text
id
college_id
media_type
image_url
source_url
license
attribution
alt_text
is_primary
width
height
verified_at
```

Preferred sources:
```text
Wikimedia Commons with compatible license
official university media assets with permission/clear reuse basis
other clearly licensed sources
```

Do not scrape/copy random Google Images results.

UI must support hero campus photo, optional gallery, alt text, and attribution where required.

## No Fake Applicant Profiles
Do not fabricate anonymized admitted-student profiles unless Evalio later owns a real, permissioned, verified outcomes dataset.

## Acceptance Criteria
- search works against DB;
- no frontend hardcoded production list;
- campus images are licensed/sourced;
- source freshness visible;
- no fabricated applicant outcomes;
- mobile cards usable.

---

# 13. TOOL 7 — COURSEWORK EVALUATOR

Route: `/tools/coursework-evaluator`

Suggested API:
```text
POST /api/v1/evaluations/coursework
```

## Goal
Evaluate rigor in school context. Do not equate “more APs” with stronger rigor when the school does not offer APs.

## Inputs
```text
curriculum_type
grade_levels
courses[]
course_levels[]
advanced_courses_available
advanced_program_types
highest_levels_available
intended_major
school_context_notes
```

## Output
```text
COURSE RIGOR

88 / 100
Strong

Challenge Level          91
Core Coverage            86
Advanced Utilization     N/A
Progression              90
Major Preparation        85

School Context
No AP/IB courses available

No penalty applied.
```

Use existing rigor logic from `SCORING_SPEC.md`.

Important:
```text
advanced opportunity not available
→ do not penalize student
```

Do not infer school offerings from country alone.

## Acceptance Criteria
- context-aware;
- intended-major preparation visible;
- unavailable advanced-course opportunity handled correctly;
- evidence explains each component.

---

# 14. TOOL 8 — SCHOLARSHIP TRACKER

Route: `/tools/scholarships`

Suggested API:
```text
GET  /api/v1/scholarships
GET  /api/v1/scholarships/{slug}
GET  /api/v1/me/scholarships
POST /api/v1/me/scholarships
PATCH /api/v1/me/scholarships/{id}
DELETE /api/v1/me/scholarships/{id}
```

## Goal
Help users discover and track scholarships, especially opportunities available to international applicants.

## Scholarship Data Model
Add if equivalent tables do not exist.

### scholarships
```text
id UUID
slug
name
provider
country_code
award_type
award_min
award_max
currency
deadline
application_open_date
renewable
international_eligible
undergraduate_eligible
citizenship_rules
residency_rules
academic_requirements
financial_need_required
major_restrictions
official_url
active
created_at
updated_at
```

### scholarship_sources
```text
id
scholarship_id
field_name
source_url
source_type
verified_at
confidence
freshness
```

### user_scholarships
```text
id
user_id
scholarship_id
status
personal_deadline
notes
created_at
updated_at
```

## Statuses
```text
SAVED
RESEARCHING
APPLYING
SUBMITTED
FINALIST
WON
REJECTED
EXPIRED
```

## Filters
```text
international eligibility
country
award amount
award type
deadline
need-based
merit-based
major
undergraduate eligibility
```

## UI
```text
Scholarship Tracker.

Find scholarships you can actually apply for.

[ Search scholarships...                 ]

Eligibility
[ International students ]

Award
[ Any ]

Deadline
[ Upcoming ]
```

Tracker summary:
```text
To Do        8
Applying     3
Submitted    4
Won          1
```

Do not show combined “potential value” if award ranges are too uncertain unless clearly labelled.

## Data Quality
Every production scholarship must have official source, verification date, deadline, eligibility source, and freshness metadata.

## Acceptance Criteria
- source-backed;
- international eligibility explicit;
- saved tracking requires auth;
- public search can be anonymous;
- deadline status deterministic;
- no invented award amounts.

---

# 15. TOOL 9 — LOR BUILDER

Route: `/tools/lor-builder`

Suggested API:
```text
POST /api/v1/lor/build
```

## Goal
Create a deterministic recommendation-letter structure from facts supplied by the recommender/student. Do not present output as AI-generated and do not invent anecdotes.

## Inputs
```text
recommender_role
student_name
relationship_context
relationship_duration
subject_or_context
qualities[]
specific_examples[]
comparative_evidence
community_evidence
academic_evidence
endorsement_strength
```

## Output
Structured framework:
```text
Opening
- relationship context
- duration
- capacity

Body 1
- academic or professional quality
- evidence

Body 2
- character/community quality
- anecdote

Body 3
- comparative evidence
- growth/progression

Closing
- endorsement
- confidence
```

May provide deterministic sentence shells such as:
```text
During [relationship context], I observed [student]
demonstrate [quality] when [specific evidence].
```

The output must make placeholders/evidence origins obvious.

## Ethics/UX
Show:
> Final wording should be reviewed and owned by the recommender.

Never fabricate awards, anecdotes, rankings, comparative claims, or relationship duration.

## Acceptance Criteria
- deterministic templates only;
- no LLM;
- no invented facts;
- all inserted claims trace to user-provided fields;
- output easily editable/copyable.

---

# 16. TOOL 10 — LOR EVALUATOR

Route: `/tools/lor-evaluator`

API:
```text
POST /api/v1/evaluations/lor
```

## Inputs
```text
lor_text
recommender_role optional
relationship_duration optional
save_raw_text false by default
```

## Output Dimensions
Use existing LOR specification.

Recommended display:
```text
LOR SIGNAL SCORE

86 / 100
Strong

Relationship Context        90
Specific Evidence           88
Academic Traits             82
Character Evidence          84
Comparative Evidence        95
Recommendation Strength     87

Generic Praise Risk
LOW
```

## Findings
Examples:
```text
✓ Relationship duration stated
✓ Two concrete anecdotes detected
✓ Comparative statement present
✓ Strong endorsement language present

⚠ Repeated generic praise
⚠ Limited community evidence
```

All findings require:
```text
rule_id
evidence
threshold
effect
confidence
```

## Persistence
Raw LOR text is not persisted by default.

## Acceptance Criteria
- deterministic;
- raw text private;
- evidence-level findings;
- no “admissions officer will love this” claims;
- no semantic personality inference.

---

# 17. EXISTING ACTIVITY EVALUATOR

Evalio already has an activity-scoring engine and should preserve it.

Suggested route:
```text
/tools/activity-evaluator
```

The UI should follow the same global tool template.

Inputs:
```text
activity name
position
organization
description
hours/week
weeks/year
duration
leadership
impact metrics
recognition
progression
founder status
```

Results:
```text
individual activity score
component breakdown
description quality
portfolio role
triggered rules
```

Do not implement a separate competing activity formula. Use `SCORING_SPEC.md`.

---

# 18. RELATED TOOLS GRAPH

Recommended related-tool cards:

```text
Essay Evaluator
→ Writing Pattern Checker
→ Essay Idea Builder

Application Evaluator
→ Coursework Evaluator
→ GPA Toolkit
→ College Explorer

College Explorer
→ Application Evaluator
→ Scholarship Tracker

LOR Builder
→ LOR Evaluator
```

Do not show more than 3 related tools per page.

---

# 19. SHARED RESULT COMPONENTS

Build reusable components:

```text
ToolHeader
ToolInputShell
ToolActionBar
ScoreCard
ScoreBreakdown
MetricRow
RuleFinding
EvidenceList
ConfidenceBadge
FreshnessBadge
SourceList
MethodologyLink
ToolHowItWorks
RelatedTools
PrivacyNotice
SaveToggle
EmptyResult
LoadingResult
ErrorResult
```

Do not duplicate equivalent components per tool.

---

# 20. SHARED RESULT LANGUAGE

Use:
```text
Strong
Moderate
Limited
High Confidence
Medium Confidence
Low Confidence
Requirement Incomplete
Very High Selectivity
Evidence Found
Insufficient Data
```

Avoid:
```text
AI thinks
Guaranteed
Perfect
Definitely admitted
Bad essay
Fake essay
Human-written
AI-written
```

---

# 21. API DESIGN RULES

All tool APIs:
- use `/api/v1`;
- use shared success/error envelope from `API_SPEC.md`;
- validate with Pydantic;
- return `engine_version`;
- return `rubric_version` where scoring applies;
- return `request_id`;
- never accept user identity from body;
- apply owner checks to saved private resources;
- return `Cache-Control: no-store` for private text analyses.

Example scoring response:
```json
{
  "data": {
    "evaluation": {
      "overall_score": 81,
      "label": "Strong",
      "confidence": "HIGH",
      "components": {},
      "metrics": {},
      "issues": []
    }
  },
  "meta": {
    "request_id": "uuid",
    "engine_version": "2.0.0",
    "rubric_version": "2.0.0"
  }
}
```

---

# 22. DATABASE ADDITIONS

Existing normalized college/applicant schema remains.

Potential additions required by this document:
```text
college_media
scholarships
scholarship_sources
user_scholarships
```

Do not add redundant tables if equivalent structures already exist. All schema changes require Alembic migrations.

---

# 23. PRIVACY

Public tools should work without login where reasonable.

Anonymous-capable:
```text
Essay Evaluator
Writing Pattern Checker
Essay Idea Builder
GPA Toolkit
Coursework Evaluator
College Explorer
Scholarship Search
LOR Builder
LOR Evaluator
```

Require account for:
```text
saved profile
saved essays
saved LORs
target colleges
scholarship tracker state
reports
application progress
```

Raw essay/LOR save checkbox:
```text
[ ] Save this text to my Evalio account
```
unchecked by default.

---

# 24. SECURITY

Apply `SECURITY.md`.

Additional tool-specific rules:
- sanitize all displayed user text;
- never render raw text via unsafe HTML;
- upload max remains product platform limit;
- no OCR;
- scholarship external URLs must be validated;
- campus image URLs must come from approved source records;
- no user-provided arbitrary remote fetch URLs;
- no raw essay/LOR logging.

---

# 25. ACCESSIBILITY

Target WCAG 2.2 AA.

Every tool:
- full keyboard support;
- labels for all inputs;
- visible focus;
- no color-only status;
- descriptive error summary;
- mobile usable at 360px;
- no essential hover-only interaction;
- result evidence accessible to screen readers.

---

# 26. RESPONSIVE RULES

Desktop:
```text
tool input/result may use 2-column layout
```

Mobile:
```text
input
↓
primary action
↓
result summary
↓
components
↓
evidence
```

Do not squeeze desktop tables into mobile width. Transform them into cards/rows.

---

# 27. LOADING STATES

Use accurate text:
```text
Analyzing essay…
Checking writing patterns…
Calculating GPA…
Evaluating coursework…
Checking college data…
Evaluating recommendation letter…
Loading scholarships…
```

Do not use fake progress percentages.

---

# 28. ERROR STATES

Errors must be human-readable.

Examples:
```text
This PDF does not contain extractable text.
Upload a text-based PDF, DOCX, TXT, or paste the text directly.
```

```text
College data is temporarily unavailable.
Your profile has not been changed.
```

```text
We could not verify this scholarship source.
```

Never expose stack traces.

---

# 29. METHODOLOGY

Every evaluator page must have:
```text
View methodology →
```

Methodology must explain:
- what is measured;
- weights;
- thresholds;
- limitations;
- current rubric version;
- what the tool cannot determine.

This is a first-class Evalio feature.

---

# 30. ANALYTICS

Allowed anonymous product analytics:
```text
tool opened
analysis completed
result expanded
methodology opened
related tool clicked
```

Do NOT send essay text, LOR text, transcript content, or financial details to analytics.

---

# 31. SEO / PAGE METADATA

Each public tool should have original Evalio metadata. Do not copy Test Ninjas titles/descriptions.

Example:
```text
<title>College Essay Evaluator | Evalio</title>
```

Description:
```text
Get transparent, rule-based feedback on measurable essay structure,
clarity, specificity, and writing patterns.
```

---

# 32. IMPLEMENTATION ORDER

Do not build all tools simultaneously.

Recommended order:
```text
T0 Shared Tool UI Foundation

T1 Essay Evaluator
T2 Writing Pattern Checker
T3 Essay Idea Builder

T4 GPA Toolkit
T5 Coursework Evaluator

T6 College Explorer + college_media
T7 Application Evaluator

T8 LOR Builder
T9 LOR Evaluator

T10 Scholarship Directory
T11 Scholarship Tracking

T12 Cross-tool integration
T13 Mobile/accessibility QA
T14 Security/privacy review
T15 Production QA
```

Activity Evaluator can be integrated whenever its existing engine milestone is ready.

---

# 33. T0 — SHARED TOOL UI FOUNDATION

Implement first:
```text
/tools
shared navigation
ToolHeader
ToolInputShell
ScoreCard
ScoreBreakdown
RuleFinding
EvidenceList
MethodologyLink
ToolHowItWorks
RelatedTools
loading/error/empty
```

Acceptance:
- no tool-specific scoring yet;
- reusable components;
- consistent Evalio UI;
- responsive.

---

# 34. IMPLEMENTATION RULE FOR CODEX

For each tool:
1. read this file;
2. read relevant scoring/rule docs;
3. inspect existing code;
4. identify already-existing engine/service/API pieces;
5. do not duplicate business logic;
6. implement only the selected tool;
7. add tests;
8. run checks;
9. inspect diff;
10. report ambiguities;
11. stop.

Do not silently implement future tools.

---

# 35. RECOMMENDED CODEX PROMPT

```text
Implement Tool T<n> from docs/TOOLS_SPEC.md.

Before coding, read:

- docs/PRD.md
- docs/TECHNICAL_DESIGN.md
- docs/DATA_SPEC.md
- docs/SCORING_SPEC.md
- docs/RULEBOOK.md
- docs/API_SPEC.md
- docs/UI_UX.md or docs/UI_UX_SPEC.md
- docs/SECURITY.md
- docs/TEST_PLAN.md
- docs/TOOLS_SPEC.md

Treat these specifications as authoritative.

Hard constraints:

- no LLM
- no AI API
- no local AI
- no machine learning
- no embeddings
- no vector DB
- no fake admission probability
- no fabricated applicant outcomes
- no invented college/scholarship data
- no scoring logic duplicated in frontend
- do not implement future tools

Design direction:

Use the referenced Test Ninjas pages only as high-level UX inspiration.
Do not clone their branding, copy, screenshots, proprietary assets,
or exact page implementation.

Evalio identity must remain:

editorial outside
+ quantitative inside
+ transparent everywhere

and every evaluator result should support:

Score
→ Evidence
→ Rule
→ Explanation

Implementation requirements:

1. inspect current code before modifying it
2. reuse existing shared UI/services/engine
3. implement API changes only when needed
4. add database migrations only when needed
5. add tests
6. run Python tests
7. run ruff
8. run mypy
9. run frontend tests/typecheck
10. run production build if frontend changed
11. inspect git diff
12. summarize changed files and unresolved issues
13. stop
```

---

# 36. GLOBAL ACCEPTANCE CRITERIA

The tools system is ready for production when:

```text
[ ] all public tools share consistent Evalio UI
[ ] no runtime AI/LLM/ML dependency exists
[ ] every scoring result is deterministic
[ ] every scoring result exposes methodology/evidence
[ ] no fake admission probability exists
[ ] no AI-authorship probability exists
[ ] international grading is not forcibly converted
[ ] school-context rigor is supported
[ ] college data is source-backed
[ ] campus imagery is licensed/source-tracked
[ ] scholarship data is source-backed
[ ] raw essay/LOR text is not persisted by default
[ ] mobile workflows work at 360px
[ ] accessibility checks pass
[ ] security checks pass
[ ] frontend contains no authoritative scoring formulas
[ ] production build passes
```

---

# 37. PRODUCT PRINCIPLE

When choosing between:
```text
more automation
```
and:
```text
more explainability
```
Evalio chooses:

> **more explainability**

When choosing between:
```text
a confident-looking guess
```
and:
```text
insufficient data
```
Evalio chooses:

> **insufficient data**
