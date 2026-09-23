# SCORING_SPEC_V2.md

# Evalio Deterministic Scoring Specification — V2
**Version:** 2.0.0  
**Status:** Proposed canonical V2 scoring specification  
**Runtime:** deterministic only; no LLM, AI API, ML, embeddings, vector DB, or admission-probability model

## 0. Core principle
> Measure what can be measured, label what is heuristic, show what is unknown, and never turn uncertainty into a fake number.

V2 distinguishes four output types:
1. **Mechanical Score** — directly measurable surface characteristics.
2. **Evidence Strength Score** — structured evidence scored by explicit rules.
3. **College Alignment Score** — applicant evidence compared with source-backed college data.
4. **Status / Compatibility** — categorical output where 0–100 would imply false precision.

## 1. Global invariants
- Numeric scores use `0–100`.
- Internal precision: at least 2 decimals; display: nearest integer unless otherwise needed.
- Clamp: `max(0, min(100, score))`.
- Missing optional evidence = `N/A`, removed from denominator.
- Missing required evidence = `REQUIREMENT_INCOMPLETE`.
- Unknown categorical facts stay `UNKNOWN`.
- Never convert `UNKNOWN -> NO`, blank -> 0, or N/A -> 0.
- Confidence is separate from score.
- Every scoring result must expose `engine_version`, `rubric_version`, `confidence`, components, evidence, and triggered rules.
- Prohibited outputs: exact admission chance, guaranteed/safety claims, AI-authorship probability, authenticity score, emotional-depth score, scholarship win probability.

### Weight redistribution
For available components only:
```text
effective_weight_i = configured_weight_i / sum(configured_weight_available)
overall = Σ(score_i × effective_weight_i)
```

## 2. Output taxonomy
| Feature | Primary V2 output | Numeric? |
|---|---|---:|
| Academics | Academic Strength | Yes |
| Coursework | Course Rigor | Yes |
| Testing | College Test Alignment | Yes |
| Activities | Activity Strength | Yes |
| Activity Description | Description Craft | Yes |
| Honors | Honor Distinction | Yes |
| Essay | Essay Craft | Yes |
| Writing Pattern Checker | Pattern Concentration | No |
| LOR Evaluator | LOR Evidence Signal | Yes |
| GPA Toolkit | Calculator result | No |
| Essay Idea Builder | Structural checklist | No |
| LOR Builder | Completeness checklist | No |
| Application Evaluator | Component matrix + Planning Category | No overall chance score |
| Financial Fit | Compatibility status | No pre-award score |
| Scholarship Tracker | Eligibility status | No win probability |
| Application Audit | Required-completion % | Yes |
| Data Quality | Confidence | Yes, supporting only |

# PART A — ACADEMICS

## 3. Academic Strength V2
```text
Academic Achievement 55%
Course Rigor         35%
Academic Trend       10%
```
Context becomes a guardrail, not a scored bonus. Major Preparation moves to college/program alignment.

## 4. Academic Achievement
### 4.1 Native scale first
For non-US grading systems, use the native school/curriculum scale. Never automatically convert percentage/IB/A-Level grades to 4.0.

### 4.2 Native-scale normalization
When valid scale bounds are known:
```text
position = (student_value - scale_min) / (scale_max - scale_min)
```
Anchors:
```text
>=0.95 -> 100
0.90   -> 94
0.85   -> 88
0.80   -> 82
0.75   -> 76
0.70   -> 70
0.65   -> 64
0.60   -> 58
<0.60  -> linearly decline toward 20 at configured floor
```
Use linear interpolation between anchors.

### 4.3 Rank corroboration
If rank/cohort size is valid:
```text
Top 1%  -> 100
Top 5%  -> 96
Top 10% -> 92
Top 20% -> 86
Top 30% -> 80
Top 50% -> 70
Below 50% -> linearly map 40–69
```
When both native performance and reliable rank exist:
```text
achievement = native_performance*0.80 + rank_evidence*0.20
```
If rank is unavailable, use native performance only. No penalty for schools that do not publish rank.

## 5. Academic Trend
Use deterministic **Theil–Sen slope** over chronological term averages:
```text
pairwise_slope(i,j) = (y_j-y_i)/(j-i)
trend_slope = median(all pairwise slopes)
```
If only one valid term: `N/A`.

Anchors in normalized percentage-point-equivalent units/term:
```text
>= +1.50       -> 95
+0.75 to 1.49  -> 88
+0.25 to 0.74  -> 80
-0.24 to 0.24  -> 75
-0.74 to -0.25 -> 65
-1.49 to -0.75 -> 52
<= -1.50       -> 35
```

# PART B — COURSEWORK

## 6. Course Rigor V2
```text
Challenge vs Opportunity 55%
Core Academic Coverage   20%
Advanced Opportunity Use 15%
Progression              10%
```

### 6.1 Challenge vs opportunity
```text
highest available level in >=80% relevant areas -> 95
60–79% -> 85
40–59% -> 72
20–39% -> 58
<20%   -> 42
```
If a school has only one course level, that area is treated as the highest available level.

### 6.2 Core coverage
```text
all expected areas maintained -> 95
one minor gap                 -> 80
one major gap                 -> 60
multiple major gaps           -> 35
```

### 6.3 Advanced opportunity use
When advanced options exist:
```text
>=80% -> 95
60–79 -> 85
40–59 -> 70
20–39 -> 55
1–19  -> 40
0     -> 25
```
When no advanced options exist: `N/A`, remove from denominator.

### 6.4 Progression
```text
clear increasing challenge -> 95
mostly stable challenge    -> 80
mixed progression          -> 65
declining rigor            -> 40
```

### 6.5 Major Preparation
Separate status:
```text
STRONG / ADEQUATE / LIMITED / GAP / N/A
```
Used only when the target major/program has a configured prerequisite map.

# PART C — TESTING

## 7. College Test Alignment V2
Testing is college-specific and excluded from universal profile scoring.

### 7.1 With directly reported P25/P50/P75
```text
P25 -> 60
P50 -> 78
P75 -> 92
```
Piecewise linear interpolation.
Above P75: interpolate from 92 to 100 at the test maximum.

Below P25:
```text
span = max(P75-P25, minimum_span)
SAT minimum_span = 80
ACT minimum_span = 3

score = 60 - 30*((P25-applicant)/span)
```
Clamp lower tail to 20.

### 7.2 Median absent
Interpolate directly `P25 -> 60` to `P75 -> 92`. Never infer median.

### 7.3 Policy behavior
```text
OPTIONAL + no score -> N/A, no penalty
REQUIRED + no score -> REQUIREMENT_INCOMPLETE
BLIND/NOT_ACCEPTED -> EXCLUDED
PROGRAM_DEPENDENT -> resolve target program; otherwise TEST_POLICY_UNKNOWN
```

# PART D — ACTIVITIES

## 8. Individual Activity Strength V2
```text
Responsibility & Ownership 25%
Impact & Outcomes          25%
Initiative                 20%
Sustained Commitment       20%
Growth / Progression       10%
```
No direct prestige, audience-size, founder-title, or organization-name score.

## 9. Responsibility & Ownership
```text
basic participation                     -> 30
consistent contributor                  -> 50
defined responsibility                  -> 65
owns a project/function                 -> 80
sustained organizational responsibility -> 92
exceptional sustained ownership         -> 98
```
Title alone cannot exceed 65.

## 10. Impact & Outcomes
```text
no clear effect evidence                  -> 30
primarily self-development                -> 45
concrete contribution                     -> 60
specific output/process improvement       -> 75
meaningful identifiable outcome           -> 88
sustained exceptional outcome             -> 96
```
Numbers such as users/customers/revenue/participants/downloads improve **evidence confidence**, not impact score directly.

## 11. Initiative
```text
assigned tasks only               -> 30
self-directed contribution        -> 50
improved existing process         -> 68
started project/subproject        -> 85
built sustained program/product   -> 95
```
Founder without concrete creation evidence: max 55.

## 12. Sustained Commitment
Duration:
```text
<2 months   30
2–5         45
6–11        60
12–23       75
24–35       88
36+         95
```
Intensity:
```text
<1 hr/wk 35
1–2      50
3–5      70
6–8      85
9–10     92
>10      95
```
No additional score beyond 10 hours/week.
```text
sustained_commitment = duration*0.75 + intensity*0.25
```
Family responsibilities and paid work use the same framework.

If simultaneous extracurricular hours exceed 70/week: warning only, no automatic score reduction.

## 13. Growth / Progression
```text
no progression evidence        -> 40
some added responsibility      -> 60
clear advancement              -> 82
multiple levels of advancement -> 95
```

## 14. Activity Portfolio
Keep current aggregation until better calibration evidence exists:
```text
#1 30%
#2 25%
#3 20%
#4 15%
#5+ 10% combined average
```
Renormalize if fewer activities. No activity-count bonus.

# PART E — ACTIVITY DESCRIPTION

## 15. Description Craft V2
```text
Action Clarity                    30%
Specificity                       25%
Responsibility/Outcome Evidence   25%
Redundancy Control                10%
Compliance/Conciseness            10%
```
Character utilization itself is not quality. Within limit = full compliance; over limit = penalty; low utilization = feedback only.

Action clarity:
```text
strong action first 5 tokens  -> 95
first 10                     -> 85
clear action later           -> 72
weak participation dominant  -> 55
no action                    -> 35
```

Responsibility/outcome evidence:
```text
clear responsibility + outcome -> 95
responsibility only             -> 80
clear output only               -> 72
generic contribution            -> 50
no evidence                     -> 30
```

Title/description overlap:
```text
<20% -> 100
20–39 -> 90
40–59 -> 75
60–79 -> 55
80%+ -> 40
```

# PART F — HONORS

## 16. Honor Distinction V2
```text
Scope       30%
Selectivity 30%
Placement   30%
Recurrence  10%
```
Major/academic relevance is metadata only and cannot alter award strength.

Scope:
```text
school 25
local 40
regional 58
state/province 72
national 88
international 96
```

Selectivity:
```text
open/>50% -> 30
top 50%   -> 45
top 25%   -> 60
top 10%   -> 78
top 5%    -> 88
top 1%    -> 96
unknown   -> N/A, redistribute, lower confidence
```

Placement:
```text
participant/finalist 35
honorable mention    50
top 10               65
top 5                75
3rd                  84
2nd                  90
1st                  96
```

Recurrence:
```text
single occurrence -> 50
repeated -> 75
multi-year repeated distinction -> 92
```

# PART G — ESSAY

## 17. Essay Craft Score V2
Replaces `Mechanical Essay Score`.

```text
Compliance                 10%
Sentence Control           25%
Structural Balance         20%
Specificity Signals        20%
Repetition & Style Hygiene 25%
```

It does **not** score authenticity, emotional depth, semantic reflection quality, personality, or admissions appeal.

## 18. Compliance
Start 100.
```text
1–10 words over/under  -15
11–25                  -30
26–50                  -50
51+                    -80
```
No semantic prompt-fit score unless an explicit deterministic prompt checklist exists.

## 19. Sentence Control
Start 100:
```text
31–40 words -1 each max -8
41–50       -2 each max -10
>50         -4 each max -16
fragment proxy -2 each max -8
very high passive proxy up to -8
```
Flesch Reading Ease is diagnostic only.

## 20. Structural Balance
Base 70:
```text
3–8 paragraphs                      +8
reasonable balance                  +6
opening <=35%                       +4
distinct ending paragraph           +4
transition diversity                +4
one paragraph >=250 words          -20
paragraph >45% of essay            -10
3+ paragraphs <15 words             -5
```
Clamp 0–100.

## 21. Specificity Signals
Categories:
```text
numbers
dates/time
location/place
named project/organization
dialogue
measurable outcome
concrete event marker
specific object/detail
```
Per 100 words:
```text
0–0.49    -> 35
0.50–0.99 -> 50
1.00–1.99 -> 65
2.00–2.99 -> 80
3.00–3.99 -> 90
4.00+     -> 95
```
4+ distinct categories: +5. Cap 100.

## 22. Repetition & Style Hygiene
Start 100:
```text
cliche phrase              -3 each max -15
filler phrase              -2 each max -12
repeated 3+ word phrase    -2 each max -12
overused transition family up to -8
repeated sentence opening  up to -8
excessive formal filler    up to -6
```

## 23. Essay Diagnostic Signal Panel
Diagnostic only; excluded from Essay Craft score.

Reflection Coverage:
```text
NONE / CONCENTRATED / DISTRIBUTED
```

Lexical variation:
```text
>=100 tokens -> MATTR window 50
60–99        -> MATTR window 25, LOW confidence
<60          -> N/A
```
Do not map MATTR to 0–100 without a calibrated corpus.

Readability: display Flesch diagnostic only.

Sentence rhythm:
```text
VERY_UNIFORM / UNIFORM / MIXED / VARIED / HIGHLY_VARIABLE
```

Personal anchoring:
```text
LOW / MODERATE / HIGH
```
This is not authenticity.

# PART H — WRITING PATTERN CHECKER

## 24. Pattern Concentration V2
Primary output:
```text
LOW / MODERATE / HIGH / INSUFFICIENT_TEXT
```
Candidate deterministic signals include sentence/paragraph uniformity, repeated n-grams, transition overuse, cliche/filler density, lexical variation, specific/named/numeric detail density, sentence-opening repetition, formality load, passive proxy, hedging, and punctuation diversity.

Signal severity weights:
```text
LOW 1
MEDIUM 2
HIGH 3
```
```text
weighted_trigger_ratio = triggered_weight / applicable_max_weight
<0.20 -> LOW
0.20–0.39 -> MODERATE
>=0.40 -> HIGH
```
Mandatory disclaimer:
> This tool identifies measurable writing patterns. It cannot determine who or what wrote the text.

# PART I — LOR

## 25. LOR Evidence Signal V2
```text
Relationship & Vantage Point  15%
Concrete Evidence/Anecdotes   25%
Academic/Intellectual         15%
Character/Community           15%
Comparative Distinction       10%
Endorsement Strength          10%
Contextualization              5%
Information Gain              5%
```
Generic-praise penalty overlay: `0 to -10`.

Relationship:
```text
absent 30
role only 50
role+duration 70
role+duration+instructional context 85
detailed sustained context 95
```

Concrete evidence:
```text
0 examples 25
1 55
2 75
3 88
4+ 95
```
Repeated same anecdote counts once.

Comparative evidence includes explicit patterns such as `top X%`, `among the strongest`, `in my X years`, `among X students`.

# PART J — NON-SCORED BUILDERS/CALCULATORS

## 26. GPA Toolkit
No quality score. Return native average, weighted/unweighted GPA if applicable, credits, method, and formula. 4.0 conversion only when user explicitly selects a documented conversion method.

## 27. Essay Idea Builder
No idea-quality score. Return structural coverage checklist:
```text
specific moment
tension/question
personal stake
change/reflection path
prompt requirement
```

## 28. LOR Builder
No pre-letter quality score. Return completeness checklist:
```text
relationship context
concrete anecdote
academic evidence
character evidence
comparative evidence
endorsement
```

# PART K — COLLEGE EVALUATION

## 29. College-Specific Evaluator V2
Do not use one universal `Application Strength 0–100` as the primary result.

Return:
```text
Academic Alignment
Course Rigor
Testing
Activities
Honors
Essay Craft
LOR Evidence
Requirements
Financial Compatibility
Selectivity Risk
Data Confidence
Planning Category
```

## 30. Academic Alignment
```text
Academic Achievement 45%
Course Rigor         30%
Testing Alignment    15%
Major Preparation    10%
```
Optional absent testing = N/A and redistribute. Required missing test = REQUIREMENT_INCOMPLETE. Unmapped major preparation = N/A.

## 31. CDS factor importance
Display:
```text
VERY_IMPORTANT / IMPORTANT / CONSIDERED / NOT_CONSIDERED / UNKNOWN
```
An internal ordering weight may be used **for explanation priority only**:
```text
1.00 / 0.70 / 0.35 / 0.00 / null
```
Never claim these are official college admission weights.

## 32. Selectivity Risk
Source specificity order:
```text
program+international
international
program
overall institution
```
Bands:
```text
<5% EXTREME
5–9.99 VERY_HIGH
10–19.99 HIGH
20–39.99 MODERATE_HIGH
40–59.99 MODERATE
>=60 LOWER
unknown UNKNOWN
```
For an international applicant with only overall rate, use it only as institution-level selectivity, cap planning-category confidence at MEDIUM, and state international-specific rate unavailable.

## 33. Planning Category
Allowed:
```text
HIGH_REACH / REACH / COMPETITIVE / LIKELY_ISH / INSUFFICIENT_DATA
```
Rules:
```text
EXTREME -> HIGH_REACH

VERY_HIGH + alignment <90 -> HIGH_REACH
VERY_HIGH + alignment >=90 -> REACH

HIGH + alignment <85 -> REACH
alignment <65 -> REACH

alignment >=70
+ selectivity MODERATE_HIGH/MODERATE
+ requirements complete
-> COMPETITIVE

selectivity MODERATE/LOWER
+ alignment >=85
+ requirements complete
+ confidence not LOW
-> LIKELY_ISH

LOW data confidence or critical missing target-college facts
-> INSUFFICIENT_DATA
```
Never show `SAFETY`, `GUARANTEED`, or `LIKELY_ADMITTED`.

# PART L — FINANCIAL

## 34. Financial Compatibility V2
Pre-award output is categorical:
```text
KNOWN_AFFORDABLE
POTENTIALLY_AFFORDABLE
FUNDING_GAP
HIGH_RISK
INCOMPATIBLE
INSUFFICIENT_DATA
```
Use published COA, family budget, international aid policy, need-awareness, verified full-need status, verified merit aid, and freshness. Do not invent net price.

Post-award:
```text
net_price = COA - grants - scholarships
annual_gap = net_price - family_budget
```
Do not subtract loans or work-study as grant aid.

# PART M — SCHOLARSHIPS

## 35. Scholarship Eligibility
No win probability.
```text
ELIGIBLE
POSSIBLY_ELIGIBLE
NOT_ELIGIBLE
INSUFFICIENT_DATA
```
Evaluate explicit criteria only: citizenship/international eligibility, degree level, major, GPA, class year, residency, deadline, and legally relevant age. Any hard failure -> NOT_ELIGIBLE. Unknown criterion with no known failure -> POSSIBLY_ELIGIBLE.

# PART N — APPLICATION AUDIT

## 36. Required Completion
Only required materials enter denominator:
```text
completion = completed_required / total_required
```
Optional items are excluded.
Statuses:
```text
COMPLETE / MISSING_REQUIRED / PENDING / DEADLINE_PASSED / NOT_APPLICABLE
```

# PART O — PROFILE SUMMARY

## 37. Profile Evidence Index
Preferred UI: show dimensions separately rather than one headline index.

If a single internal summary is retained:
```text
Academics    50%
Activities   20%
Honors       10%
Essay Craft  10%
LOR Evidence 10%
```
Testing is excluded because it is college-specific.

Mandatory disclaimer:
> Internal Evalio profile summary. Not an admission probability or university rating.

# PART P — CONFIDENCE

## 38. College Evaluation Confidence
```text
Input Completeness   30%
Source Authority     30%
Source Freshness     25%
Metric Applicability 15%
```
Source authority anchors:
```text
official university / official CDS 100
IPEDS / College Scorecard           95
official Common App                 90
source-preserving verified archive  75
manually verified secondary source  60
unverified                          25
```
Band:
```text
85–100 HIGH
65–84 MEDIUM
<65 LOW
```
Caps:
```text
critical policy stale -> max MEDIUM
2+ critical fields UNKNOWN -> max LOW
international applicant + no intl-specific selectivity -> planning confidence max MEDIUM
```

## 39. Text Analysis Confidence
```text
Sample Adequacy      35%
Parsing Quality      25%
Evidence Coverage    25%
Metric Applicability 15%
```

# PART Q — STORAGE / CHANGE CONTROL

## 40. Numeric evaluation shape
```json
{
  "engine_version": "2.0.0",
  "rubric_version": "academic-2.0.0",
  "overall_score": 88.42,
  "display_score": 88,
  "components": {},
  "signals": {},
  "rules_triggered": [],
  "metrics": {},
  "confidence": {"score": 91, "band": "HIGH"},
  "evaluated_at": "ISO-8601"
}
```

Status-only tools may omit `overall_score`:
```json
{
  "engine_version": "2.0.0",
  "rubric_version": "financial-fit-2.0.0",
  "status": "POTENTIALLY_AFFORDABLE",
  "evidence": {},
  "confidence": {"score": 76, "band": "MEDIUM"}
}
```

## 41. Golden fixture policy
V2 is calibrated using deterministic fixtures, not trained on historical admission outcomes.

Required fixture families:
- high grades/high rigor;
- same grades, no advanced courses offered;
- international native grading;
- strong title/no activity evidence;
- family responsibility;
- large audience/shallow impact;
- meaningful small-scale impact;
- honor selectivity unknown;
- essay repeated reflection markers;
- low readability but controlled prose;
- short essay sample;
- optional test missing;
- required test missing;
- generic vs specific LOR;
- need-aware full-need college;
- stale/missing international data.

Every threshold gets:
```text
threshold - epsilon
threshold
threshold + epsilon
```

## 42. Versioning
Any change to a threshold, weight, rule, detector, or score mapping requires:
- rubric-version increment;
- golden-test update;
- regression comparison;
- changelog entry.

Never overwrite stored V1 evaluations.

## 43. Rationale note
The architecture is evidence-informed, but all numeric Evalio weights remain **internal product choices**, not official university admission formulas. College factor-importance data should be presented as source-backed context, not reverse-engineered probabilities.
