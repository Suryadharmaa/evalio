# SCORING_SPEC.md

# Deterministic Admissions Scoring Specification

**Version:** 2.0.0  
**Purpose:** Define exact scoring behavior for implementation.  
**Important:** These scores are internal product metrics, not official university admissions ratings.

---

## 1. Global Scoring Principles

All component scores use:

```text
0–100
```

unless explicitly defined otherwise.

Interpretation:

```text
90–100  Exceptional internal signal
80–89   Strong
70–79   Competitive
60–69   Moderate
50–59   Limited
0–49    Weak / insufficient signal
```

These labels describe internal rubric performance only.

They are not probabilities of admission.

---

## 2. General Score Rules

### Clamp

Every component score:

```python
score = max(0, min(100, score))
```

### Rounding

Internal:

- keep at least 2 decimal places.

Displayed:

- round to nearest integer unless comparison needs decimals.

### Missing Data

Missing optional data does not become zero.

Use:

```text
N/A
```

and remove that factor from the applicable weighted denominator.

Missing required college data becomes:

```text
REQUIREMENT_INCOMPLETE
```

not zero.

---

# PART A — ACADEMIC SCORING

## 3. Academic Strength Score

Default:

```text
Academic Performance       45%
Course Rigor               30%
Academic Trend             10%
Academic Context           10%
Major Preparation           5%
```

Formula:

```text
academic_strength =
performance * 0.45 +
rigor * 0.30 +
trend * 0.10 +
context * 0.10 +
major_preparation * 0.05
```

---

## 4. Academic Performance Score

For curricula with percentage grades, use normalized school-scale position instead of forced US GPA conversion.

### 4.1 If school maximum/minimum are known

```text
normalized =
(student_average - scale_min) /
(scale_max - scale_min)
```

Then map:

```text
>= 0.95  -> 100
>= 0.90  -> 94
>= 0.85  -> 88
>= 0.80  -> 82
>= 0.75  -> 76
>= 0.70  -> 70
>= 0.65  -> 64
>= 0.60  -> 58
<  0.60  -> interpolate down to 20
```

### 4.2 If percentile/rank is known

Rank percentile may modify performance:

```text
Top 1%       +6
Top 5%       +5
Top 10%      +4
Top 20%      +2
Top 30%      +1
Unknown       0
```

Final performance is capped at 100.

### 4.3 Major-subject modifier

If at least 3 relevant major-preparation courses exist:

```text
major-course average >= overall + 3 percentage points -> +3
major-course average >= overall + 1                  -> +1
major-course average within ±1                       ->  0
major-course average <= overall - 3                  -> -3
```

---

## 5. Academic Trend Score

Input:

semester averages in chronological order.

Use ordinary least squares slope over semester index.

Convert slope:

```text
slope >= +2.0 points/semester -> 100
+1.0 to +1.99                -> 90
+0.5 to +0.99                -> 82
-0.49 to +0.49               -> 75
-0.99 to -0.50               -> 65
-1.99 to -1.00               -> 50
<= -2.0                      -> 35
```

If only one semester exists:

```text
trend = N/A
```

and redistribute weight.

---

## 6. Course Rigor Score

Default dimensions:

```text
Challenge vs available curriculum    40
Core academic coverage               20
Advanced-course utilization          20
Progression                           10
Major preparation                    10
```

### 6.1 Challenge vs Available Curriculum

If school context known:

```text
took highest level in >=80% relevant core areas -> 40
60–79%                                          -> 34
40–59%                                          -> 27
20–39%                                          -> 20
<20%                                            -> 12
```

If school does not offer advanced courses, do not penalize the applicant.

### 6.2 Core Coverage

Core areas:

- language/English;
- mathematics;
- laboratory science;
- social science;
- foreign language where applicable.

Scoring:

```text
all expected core areas maintained       20
one minor gap                            16
one major gap                            11
multiple gaps                             5
```

### 6.3 Advanced Utilization

```text
>=80% of available advanced opportunities used -> 20
60–79%                                    -> 17
40–59%                                    -> 13
20–39%                                    -> 9
1–19%                                     -> 5
0% where advanced options exist           -> 2
no advanced options available             -> 16 neutral-context score
```

### 6.4 Progression

```text
clear increasing difficulty       10
mostly stable challenge             8
mixed progression                   6
declining rigor                     3
```

### 6.5 Major Preparation

```text
strong sequence / multiple relevant courses -> 10
adequate preparation                      -> 7
limited exposure                           -> 4
major prerequisites missing                -> 1
```

---

# PART B — TESTING

## 7. Test Position Score

For SAT/ACT where college percentile data exists.

Given applicant score `x`, college P25 `a`, median `m`, P75 `b`:

```text
x < a - meaningful_margin  -> 40 or lower
x == a                     -> 60
x == m                     -> 75
x == b                     -> 90
x > b                      -> up to 100
```

Use linear interpolation between anchors.

Recommended SAT meaningful margin:

```text
100 points
```

Recommended ACT meaningful margin:

```text
4 points
```

### Test Optional

If applicant has no score:

```text
testing = N/A
```

No penalty.

### Test Required

If no valid score:

```text
REQUIREMENT_INCOMPLETE
```

### Test Blind / Not Accepted

Testing contribution:

```text
excluded
```

---

# PART C — ACTIVITY SCORING

## 8. Individual Activity Score

Dimensions:

```text
Impact                  25
Leadership              20
Duration                15
Initiative              15
Time Commitment         10
Recognition             10
Progression              5
```

Total:

```text
100
```

---

## 9. Activity Impact

Impact must be supported by entered evidence.

```text
No identifiable effect                         2
Self-development only                          5
Small-group contribution                       8
Meaningful impact on 10–49 people             11
Meaningful impact on 50–199                   15
Meaningful impact on 200–999                  19
Meaningful impact on 1,000+                   22
Exceptional independently verifiable impact   25
```

Do not infer impact from title alone.

---

## 10. Leadership

```text
No leadership / participant                 2
Informal responsibility                     6
Defined operational responsibility         10
Team/project lead                          14
Executive role / captain / president       17
Founder with demonstrated responsibility   18
Founder + sustained team/operations        20
```

A title without evidence caps leadership at:

```text
10
```

---

## 11. Duration

Use active months:

```text
< 2 months         2
2–5 months         5
6–11 months        8
12–23 months      11
24–35 months      13
36+ months        15
```

Seasonal annual activities may accumulate active months across years.

---

## 12. Initiative

```text
Only assigned tasks                         2
Occasional self-directed contribution       5
Improved existing process                   9
Started a new project/subproject           12
Created organization/product/program       15
```

Founder title without concrete creation evidence:

```text
max 8
```

---

## 13. Time Commitment

Use average hours/week with sustainability cap.

```text
<1                 2
1–2                4
3–5                6
6–10               8
11+                10
```

Anti-gaming:

Total weekly activity hours across all simultaneous activities must be plausibility-checked.

Recommended warning:

```text
> 70 hours/week extracurricular total
```

Flag only; do not automatically accuse user of false reporting.

---

## 14. Recognition

```text
None                             1
School/local recognition         3
Regional                         5
State/province                   7
National                         9
International                   10
```

Scope requires evidence fields when possible.

---

## 15. Progression

```text
No progression                 1
Some added responsibility      3
Clear advancement              4
Multiple levels of advancement 5
```

---

## 16. Activity Portfolio Score

Do not average all activities equally.

Sort by individual activity score descending.

Weights:

```text
#1    30%
#2    25%
#3    20%
#4    15%
#5+   10% combined
```

For 5+:

```text
combined_score = average(scores[4:])
```

If fewer than 4 activities exist, renormalize the used weights.

Do not penalize simply for having fewer than 10 activities.

---

# PART D — HONORS

## 17. Honor Score

Dimensions:

```text
Scope              30
Selectivity        25
Placement          20
Academic Relevance 15
Recurrence         10
```

---

## 18. Honor Scope

```text
School         8
Local         12
Regional      18
State         22
National      27
International 30
```

---

## 19. Honor Selectivity

If participant/selection information known:

```text
open participation / unclear          5
selected top 50%                     10
top 25%                              15
top 10%                              20
top 5%                               23
top 1%                               25
```

If unknown:

```text
8
```

Do not infer selectivity from award name.

---

## 20. Placement

```text
participant/finalist only    5
honorable mention            8
top 10                      12
top 5                       15
3rd                         17
2nd                         18
1st                         20
```

---

# PART E — ESSAY

## 21. Essay Mechanical Score

Default weights:

```text
Compliance             10%
Clarity                 15%
Structure               15%
Specificity Signals     15%
Reflection Signals      15%
Voice Indicators        10%
Sentence Variety        10%
Style Hygiene           10%
```

This is explicitly called:

```text
Mechanical Essay Score
```

It is not an evaluation of emotional quality or authenticity.

---

## 22. Compliance

Start:

```text
100
```

Penalties:

```text
word count above limit:
1–10 words      -15
11–25           -30
26–50           -50
51+             -80

below minimum:
1–10 words      -15
11–25           -30
26–50           -50
51+             -80
```

If a required prompt is missing from metadata:

```text
informational warning only
```

unless the product has a precise prompt-specific rule.

---

## 23. Clarity

Start:

```text
100
```

Penalties:

```text
sentence 31–40 words       -1 each, max -8
sentence 41–50 words       -2 each, max -10
sentence >50 words         -4 each, max -16
filler phrase              -1 each, max -10
very high passive pattern  up to -8
fragment-like sentence     -2 each, max -8
```

Readability modifier:

Flesch Reading Ease:

```text
50–80        +0
35–49        -4
20–34        -8
<20          -12
>80          -2 only if text also shows low sentence variety
```

Do not reward artificially simple writing.

---

## 24. Structure

Start:

```text
70
```

Adjustments:

```text
3–8 paragraphs                         +8
paragraph-length balance reasonable    +6
opening paragraph not >35% of essay    +4
ending paragraph present               +4
transition diversity                   +4
extreme one-paragraph essay           -20
paragraph >45% of total words         -10
multiple paragraphs <15 words          -5
```

Maximum:

```text
100
```

Minimum:

```text
0
```

---

## 25. Specificity Signals

Count unique specificity categories:

- numbers;
- dates/time;
- location/place references;
- named project/organization;
- dialogue;
- measurable outcome;
- concrete event markers.

Normalize per 100 words.

Suggested base:

```text
0.0–0.5 signals/100 words -> 35
0.5–1.0                   -> 50
1.0–2.0                   -> 65
2.0–3.0                   -> 80
3.0–4.0                   -> 90
4.0+                       -> 95
```

Diversity bonus:

```text
>=4 distinct categories +5
```

Cap:

```text
100
```

Repeated identical signal types have diminishing contribution.

---

## 26. Reflection Signals

Reflection marker dictionary is maintained in versioned data.

Examples:

```text
I realized
I learned
I began to understand
I discovered
I noticed
I questioned
looking back
since then
this taught me
because of this
```

Contribution for identical normalized marker:

```text
1st occurrence   1.00
2nd              0.50
3rd              0.25
4th+             0.00
```

Calculate effective unique-weighted markers per 100 words.

Map:

```text
0                    -> 25
0.01–0.49            -> 40
0.50–0.99            -> 55
1.00–1.49            -> 70
1.50–1.99            -> 80
2.00–2.99            -> 90
3.00+                 -> 95
```

Distribution bonus:

Reflection found in at least 2 different essay quartiles:

```text
+3
```

Reflection found in at least 3 quartiles:

```text
+5
```

Cap:

```text
100
```

This score measures textual indicators only.

---

## 27. Voice Indicators

Start:

```text
60
```

Adjust:

```text
first-person presence appropriate          +8
sentence-length variation healthy          +8
at least one direct quote/dialogue          +4
rhetorical variation                        +4
contraction use where natural               +2
generic phrase density high               -10
extreme repeated sentence openings         -8
excessive formal filler                     -6
```

Do not label this "authenticity".

---

## 28. Sentence Variety

Use sentence lengths.

Calculate:

- mean;
- standard deviation;
- proportion under 8 words;
- proportion 9–20;
- proportion 21–35;
- proportion >35.

Suggested score:

```text
balanced distribution                     85
healthy stddev and multiple length bands  +10
>60% sentences same length band           -15
>25% sentences >35 words                  -15
>35% sentences <8 words                   -10
```

Clamp 0–100.

---

## 29. Style Hygiene

Start:

```text
100
```

Penalties:

```text
cliché phrase                    -3 each, max -15
filler phrase                    -2 each, max -12
repeated 3+ word phrase          -2 each, max -12
overused content word            -1 each, max -8
excessive adverb pattern         up to -6
redundant transition pattern     up to -6
```

No grammar AI may be used.

---

## 30. Essay Rule Priority

Priority score:

```text
priority =
severity_weight *
score_impact_weight *
confidence_weight
```

Suggested mappings:

Severity:

```text
CRITICAL  4
HIGH      3
MEDIUM    2
LOW       1
```

Confidence:

```text
HIGH      1.0
MEDIUM    0.7
LOW       0.4
```

Return top 5 issues by default.

---

# PART F — ACTIVITY DESCRIPTION

## 31. Activity Description Score

Dimensions:

```text
Character Efficiency      20
Action Clarity             25
Impact Evidence            25
Specificity                15
Redundancy Control         15
```

---

## 32. Character Efficiency

Given max characters:

```text
usage >=90% and no truncation  -> 100
80–89%                         -> 90
65–79%                         -> 80
50–64%                         -> 68
<50%                           -> 55
over limit                     -> 20
```

High character use does not compensate for poor content.

---

## 33. Action Clarity

Action verbs detected near beginning:

```text
strong action in first 5 tokens          -> 95
strong action in first 10 tokens         -> 85
action verb later                        -> 72
weak participation phrase dominant       -> 55
no identifiable action                   -> 35
```

---

## 34. Impact Evidence

```text
quantified measurable impact             -> 95
clear concrete nonnumeric impact          -> 82
specific responsibility                  -> 70
generic contribution                     -> 52
no impact/responsibility evidence         -> 35
```

---

## 35. Redundancy

Compare normalized position title with description.

Token overlap:

```text
<20%     -> 100
20–39%   -> 90
40–59%   -> 75
60–79%   -> 55
80%+     -> 40
```

---

# PART G — LOR SIGNAL ANALYSIS

## 36. LOR Score

Dimensions:

```text
Relationship Context      20
Specific Evidence         30
Academic Traits           15
Community Traits          10
Comparative Evidence      15
Generic Praise Control    10
```

The tool must call this:

```text
LOR Signal Score
```

not recommendation quality certainty.

---

## 37. Relationship Context

```text
relationship absent                      30
role identified only                     50
role + duration                          70
role + duration + instructional context  85
detailed sustained context               95
```

---

## 38. Specific Evidence

Use count and distribution of concrete examples.

```text
0 examples    -> 25
1             -> 55
2             -> 75
3             -> 88
4+            -> 95
```

Repeated references to the same example count once.

---

# PART H — COLLEGE EVALUATION

## 39. College Evaluation Dimensions

Do not collapse to one acceptance probability.

Return:

```text
Academic Alignment
Application Strength
Requirements Fit
Financial Fit
Selectivity Risk
Data Confidence
Planning Category
```

---

## 40. CDS Importance Mapping

Internal mapping:

```text
VERY_IMPORTANT = 1.00
IMPORTANT      = 0.70
CONSIDERED     = 0.35
NOT_CONSIDERED = 0.00
UNKNOWN        = null
```

These are product weights, not official college weights.

---

## 41. Academic Alignment

Inputs may include:

- grades/rank;
- rigor;
- SAT/ACT;
- major preparation.

For standardized metrics with college ranges:

```text
well below lower range   35
below lower range        50
at lower range           60
within range             70
near median              78
above median             85
at/above upper range     92
well above upper range   97
```

For missing standardized data:

- exclude if optional;
- mark incomplete if required.

---

## 42. Selectivity Risk

Based on overall published admit rate:

```text
<5%        EXTREME
5–9.99%    VERY_HIGH
10–19.99%  HIGH
20–39.99%  MODERATE_HIGH
40–59.99%  MODERATE
60%+       LOWER
unknown    UNKNOWN
```

This is institution-level selectivity, not applicant probability.

---

## 43. Planning Category

Recommended deterministic rules:

### HIGH_REACH

Any:

```text
selectivity EXTREME
```

or:

```text
selectivity VERY_HIGH and academic alignment < 90
```

### REACH

Any:

```text
selectivity VERY_HIGH
selectivity HIGH and academic alignment < 85
academic alignment < 65
```

### COMPETITIVE

Typical:

```text
academic alignment >= 70
and selectivity MODERATE_HIGH or MODERATE
and no critical requirement gap
```

### LIKELY_ISH

Only if:

```text
selectivity MODERATE or LOWER
academic alignment >= 85
requirements complete
```

Never show `SAFETY`.

If data confidence is LOW:

```text
INSUFFICIENT_DATA
```

may override.

---

# PART I — PROFILE STRENGTH INDEX

## 44. PSI

Default internal overview:

```text
Academics          35%
Activities         25%
Honors             10%
Essay Signals      15%
LOR Signals        10%
Testing             5%
```

Missing optional component weights are redistributed.

The PSI is:

```text
not college-specific
not admission probability
not official
```

Display disclaimer every time PSI is shown.

---

# PART J — CONFIDENCE

## 45. Evaluation Confidence

Calculate points:

```text
profile completeness         0–35
source freshness             0–25
college-data completeness    0–20
metric reliability           0–20
```

Map:

```text
85–100 HIGH
65–84  MEDIUM
0–64   LOW
```

If critical source data is stale:

maximum confidence:

```text
MEDIUM
```

If multiple critical fields are unknown:

maximum:

```text
LOW
```

---

# PART K — SCORE STORAGE

## 46. Required Stored Evaluation Shape

```json
{
  "engine_version": "1.0.0",
  "rubric_version": "essay-1.0.0",
  "overall_score": 81.25,
  "display_score": 81,
  "components": {},
  "rules_triggered": [],
  "metrics": {},
  "confidence": "HIGH",
  "evaluated_at": "ISO-8601"
}
```

---

# PART L — CHANGE CONTROL

## 47. Changing Thresholds

Any change that can alter a score requires:

1. rubric version increment;
2. regression test update;
3. changelog entry;
4. golden fixture comparison.

Do not silently modify scoring thresholds.

---

## 48. Prohibited Scoring

The engine must never numerically score:

- race;
- ethnicity;
- religion;
- sex;
- sexual orientation;
- disability;
- political affiliation;
- protected medical status;
- subjective physical appearance.

The engine must not claim to measure:

- true authenticity;
- kindness;
- emotional depth;
- admissions-officer opinion;
- acceptance probability.



---

# WEB V2 ADDENDUM

## Authoritative Runtime

All authoritative scoring is computed by the Python server-side deterministic engine.

Frontend TypeScript may calculate non-authoritative display helpers such as live word count, but must not independently recreate final score formulas.

## Anonymous Evaluations

Anonymous essay/activity-description analyses use exactly the same rubric as authenticated analyses.

Persistence status must never affect score.

## API Representation

All score responses must include:

```text
engine_version
rubric_version
overall_score
components
triggered_rules
confidence
```

No web endpoint may add an acceptance-probability field unless a future separately validated methodology is formally specified.

## Web Display

The UI may round scores for display, but raw internal score precision must remain available in API/storage for reproducibility.
