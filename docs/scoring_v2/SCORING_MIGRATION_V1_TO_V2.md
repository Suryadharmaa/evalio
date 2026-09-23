# SCORING_MIGRATION_V1_TO_V2.md

# Evalio Scoring Migration — V1 to V2
**Target engine:** `2.0.0`  
**Strategy:** parallel-version migration; never silently overwrite V1

## 0. Objective
Move Evalio from V1 scoring to V2 while preserving reproducibility of all historical evaluations.

V1 remains readable and reproducible.
V2 becomes the new evaluation engine only after regression validation.

## 1. Version map
Create:
```text
engine_version = 2.0.0

academic-2.0.0
coursework-2.0.0
testing-2.0.0
activity-2.0.0
activity-description-2.0.0
honor-2.0.0
essay-craft-2.0.0
writing-patterns-2.0.0
lor-2.0.0
college-alignment-2.0.0
financial-fit-2.0.0
scholarship-eligibility-2.0.0
application-audit-2.0.0
confidence-2.0.0
profile-evidence-2.0.0
```
Never rewrite stored V1 version fields.

## 2. Semantic changes by domain

### Academics
V1:
```text
Performance 45
Rigor 30
Trend 10
Context 10
Major Prep 5
```
V2:
```text
Achievement 55
Rigor 35
Trend 10
```
Context becomes guardrail. Major preparation moves to college/program alignment.

### Activities
V1 uses audience-count impact anchors.
V2 removes audience-size scoring and uses:
```text
Responsibility 25
Impact 25
Initiative 20
Sustained Commitment 20
Growth 10
```

### Activity Description
V1 rewards character utilization directly.
V2 treats character limit as compliance only. Low utilization is feedback, not a penalty.

### Honors
V1 includes Academic Relevance and uses a default selectivity value when unknown.
V2 removes relevance from distinction score and makes unknown selectivity `N/A`.

### Essay
V1 uses `Mechanical Essay Score` with Reflection and Voice numerical components.
V2 uses `Essay Craft Score`:
```text
Compliance
Sentence Control
Structural Balance
Specificity
Style Hygiene
```
Reflection, MATTR, readability, rhythm, and personal anchoring become diagnostics.

### Writing Pattern Checker
V2 primary output:
```text
LOW / MODERATE / HIGH / INSUFFICIENT_TEXT
```
Never AI probability.

### LOR
V2 expands evidence dimensions and uses generic praise as a penalty overlay.

### College evaluation
V2 removes one universal probability-like headline score from the primary college-specific result.
Return a component matrix + Planning Category.

### Financial
Pre-award output becomes categorical compatibility, not 0–100.

### Scholarships
Eligibility status only; never chance to win.

## 3. Database migration principles
No destructive migration.

If current generic JSON evaluation storage can represent V2, reuse it.

If schema changes are necessary, use backward-compatible nullable fields:
```text
evaluations
- id
- user_id
- evaluation_type
- engine_version
- rubric_version
- overall_score nullable
- status nullable
- label nullable
- confidence_score nullable
- confidence_band nullable
- components_json
- signals_json
- metrics_json
- created_at
```
Status-only tools must not require `overall_score`.

## 4. API migration
Every V2 response retains the shared envelope:
```json
{
  "data": {
    "evaluation": {}
  },
  "meta": {
    "request_id": "uuid",
    "engine_version": "2.0.0",
    "rubric_version": "domain-2.0.0"
  }
}
```

Numeric:
```json
{
  "overall_score": 86.42,
  "display_score": 86,
  "components": {},
  "signals": {},
  "confidence": {"score": 91, "band": "HIGH"},
  "rules": []
}
```

Status-only:
```json
{
  "status": "POTENTIALLY_AFFORDABLE",
  "evidence": {},
  "confidence": {"score": 76, "band": "MEDIUM"},
  "rules": []
}
```

Frontend must not assume `overall_score` is always present.

## 5. Frontend migration
Required terminology changes:
```text
Mechanical Essay Score -> Essay Craft Score
AI Risk / AI probability -> Pattern Concentration
```

College-specific evaluator should present:
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

Do not display exact chance/probability.

## 6. Parallel engine rollout
Recommended feature/version switch:
```text
SCORING_ENGINE_VERSION=v1|v2
```

Historical V1 results remain V1.
New V2 analysis creates a new record.

Never silently re-score saved V1 reports.

## 7. Regression harness
For each fixture run both engines and store:
```text
fixture_id
domain
v1_score_or_status
v2_score_or_status
delta_or_change
expected_reason
unexpected_change
```

Large differences are acceptable only when explained by intentional V2 semantics.

## 8. Required golden fixtures

### Academics
```text
A1 high grades + high rigor
A2 same grades + school offers no AP/IB
A3 strong grades + one downward outlier
A4 one term only
A5 international percentage scale
A6 rank unavailable by school policy
```
Assertions:
- A2 not penalized for unavailable AP/IB.
- A3 Theil–Sen trend less distorted by one outlier than OLS.
- A4 trend N/A.
- A5 no forced 4.0 conversion.
- A6 no rank penalty.

### Activities
```text
ACT1 high-status title + weak evidence
ACT2 founder + no creation evidence
ACT3 family responsibility, 15 hrs/week, 3 years
ACT4 1,000 social impressions + shallow contribution
ACT5 meaningful tutoring outcome for one student
ACT6 paid work with sustained responsibility
ACT7 >70 simultaneous weekly hours
```
Assertions:
- ACT4 does not automatically outrank ACT5.
- ACT3 and ACT6 have no category penalty.
- ACT7 returns warning only.

### Honors
```text
H1 national award + known selectivity
H2 international title + no supporting context
H3 selectivity unknown
H4 high-level award unrelated to intended major
```
Assertions:
- H3 selectivity N/A.
- H4 relevance does not reduce distinction score.

### Essay
```text
E1 "I realized" repeated 5 times
E2 equivalent essay without repeated marker
E3 high specificity + one giant paragraph
E4 low Flesch score + controlled prose
E5 50-token sample
E6 repeated transition family
```
Assertions:
- E1 gets no direct reflection-score bonus.
- E4 Flesch alone does not reduce Essay Craft.
- E5 MATTR N/A.

### Testing
```text
T1 optional + no score
T2 required + no score
T3 blind + score submitted
T4 P25/P75 only
T5 program-dependent unresolved
```

### LOR
```text
L1 generic praise only
L2 two distinct specific anecdotes
L3 comparison + recommender context
L4 same anecdote repeated
```

### Financial
```text
F1 no international aid + large need
F2 need-aware + full-need verified
F3 actual award within family budget
F4 actual award above budget
F5 stale COA
```

### College
```text
C1 <5% admit rate
C2 7% admit rate + alignment 95
C3 25% + alignment 80
C4 55% + alignment 90
C5 international rate unavailable
C6 multiple critical fields unknown
```

## 9. Threshold-boundary tests
For every numerical boundary:
```text
threshold - epsilon
threshold
threshold + epsilon
```
Examples:
```text
hours/week: 8, 9, 10, 11
selectivity: 4.99, 5.00, 9.99, 10.00
rank bands around 5%, 10%, 20%
essay word limit: exact, +1, +10, +11
MATTR sample: 59, 60, 99, 100 tokens
```

## 10. Determinism test
Same:
```text
input
rubric version
college-data snapshot
evaluation date
```
must produce equivalent normalized result, excluding:
```text
request_id
evaluated_at
runtime timing
```

## 11. Migration validation checklist
Before production defaults to V2:
```text
[ ] V2 rubrics versioned
[ ] V2 rule IDs unique
[ ] V1 stored evaluations reproducible
[ ] regression harness passes
[ ] golden fixtures pass
[ ] boundary tests pass
[ ] frontend supports status-only outputs
[ ] no frontend authoritative scoring formulas
[ ] no admission probability
[ ] no AI probability
[ ] no forced international GPA conversion
[ ] context/nonavailability guards work
[ ] confidence caps work
[ ] production build passes
```

## 12. Recommended implementation sequence
Phase 1: shared V2 framework and version registry.  
Phase 2: academics, coursework, testing.  
Phase 3: activities, activity descriptions, honors.  
Phase 4: essay, writing patterns, LOR.  
Phase 5: college alignment, financial, scholarship, application audit.  
Phase 6: frontend wording/results.  
Phase 7: full regression report.  
Phase 8: switch new-analysis default to V2.

Do not implement all domains in one unreviewed commit.

## 13. Rollback
Keep V1 path until V2 production validation is complete.

Rollback should require only:
```text
SCORING_ENGINE_VERSION=v1
```
and must not require deleting V2 evaluation rows.

## 14. Completion definition
Migration is complete when:
- new evaluations use V2;
- old evaluations retain V1;
- result surfaces show engine/rubric versions;
- methodology pages match actual implemented formulas;
- score changes are regression-explained;
- no runtime AI/ML dependency exists.
