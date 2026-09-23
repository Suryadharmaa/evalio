# RULEBOOK_V2.md

# Evalio Deterministic Rulebook — V2
**Version:** 2.0.0  
**Rule-ID policy:** existing V1 IDs are never reused for a different meaning  
**Runtime:** deterministic only

## 0. Rule schema
Every triggered rule returns:
```text
rule_id
rule_version
domain
category
severity
title
trigger
evidence
effect
message
confidence
methodology_ref
```

Severity:
```text
CRITICAL / HIGH / MEDIUM / LOW / INFO
```
Confidence:
```text
HIGH / MEDIUM / LOW
```

Rule priority:
```text
CRITICAL > HIGH > MEDIUM > LOW > INFO
```
Tie-breakers:
1. larger direct score/status impact;
2. higher confidence;
3. earlier textual position where relevant;
4. lower rule ID.

# ACADEMICS

## ACAD2-001 — Native Scale Required
Trigger:
```text
non-US grading system
and no explicit user-selected documented conversion
```
Effect:
```text
evaluate native scale
do not auto-convert to 4.0
```
Severity: INFO  
Confidence: HIGH

## ACAD2-002 — Missing Scale Bounds
Trigger:
```text
grading system not recognized
and scale bounds unavailable
```
Effect:
```text
Academic Achievement = N/A
confidence reduced
```
Severity: HIGH

## ACAD2-003 — Rank Evidence Available
Trigger:
```text
valid rank + valid cohort size
```
Effect:
```text
rank evidence may contribute up to 20% of Academic Achievement
```
Severity: INFO

## ACAD2-004 — Rank Not Published
Trigger:
```text
school/context explicitly states rank is unavailable/not published
```
Effect:
```text
no penalty
rank component excluded
```
Severity: INFO

## ACAD2-005 — Positive Robust Trend
Trigger:
```text
Theil–Sen slope >= +0.75 per term
```
Effect:
```text
trend anchor >=88 depending slope
```
Severity: INFO

## ACAD2-006 — Negative Robust Trend
Trigger:
```text
Theil–Sen slope <= -0.75 per term
```
Effect:
```text
trend <=52 depending slope
```
Severity: MEDIUM

## ACAD2-007 — Insufficient Trend History
Trigger:
```text
fewer than 2 valid terms
```
Effect:
```text
trend = N/A
redistribute weight
```
Severity: INFO

# COURSEWORK

## RIGOR2-001 — No Advanced Courses Available
Trigger:
```text
school reports zero relevant advanced opportunities
```
Effect:
```text
Advanced Opportunity Use = N/A
redistribute rigor weight
```
Severity: INFO

## RIGOR2-002 — Opportunity Context Missing
Trigger:
```text
advanced-course availability unknown
```
Effect:
```text
do not assume low utilization
confidence reduced
```
Severity: MEDIUM

## RIGOR2-003 — High Opportunity Utilization
Trigger:
```text
advanced utilization >=80%
```
Effect:
```text
Advanced Opportunity Use = 95
```
Severity: INFO

## RIGOR2-004 — Core Academic Gap
Trigger:
```text
one or more expected core academic areas absent
```
Effect:
```text
Core Academic Coverage reduced according to count/severity
```
Severity: MEDIUM or HIGH

## RIGOR2-005 — Major Preparation Gap
Trigger:
```text
target major/program has configured prerequisite
and applicant lacks it
```
Effect:
```text
Major Preparation = GAP
```
Severity: HIGH  
Note: no direct reduction to general Academic Strength.

# TESTING

## TEST2-001 — Required Test Missing
Trigger:
```text
policy == REQUIRED
and no valid accepted test
```
Effect:
```text
REQUIREMENT_INCOMPLETE
```
Severity: CRITICAL

## TEST2-002 — Optional Test Missing
Trigger:
```text
policy == OPTIONAL
and no valid score
```
Effect:
```text
Test Alignment = N/A
no penalty
```
Severity: INFO

## TEST2-003 — Test Blind
Trigger:
```text
policy in {BLIND, NOT_ACCEPTED}
```
Effect:
```text
exclude testing entirely
```
Severity: INFO

## TEST2-004 — Program Policy Unresolved
Trigger:
```text
policy == PROGRAM_DEPENDENT
and target-program policy unavailable
```
Effect:
```text
TEST_POLICY_UNKNOWN
confidence reduced
```
Severity: HIGH

## TEST2-005 — Median Not Reported
Trigger:
```text
P25 and P75 available
P50 unavailable
```
Effect:
```text
interpolate directly P25 -> P75
do not infer median
```
Severity: INFO

# ACTIVITIES

## ACT2-001 — Title Without Responsibility Evidence
Trigger:
```text
high-status title present
but responsibility evidence weak/absent
```
Effect:
```text
Responsibility & Ownership max = 65
```
Severity: MEDIUM

## ACT2-002 — Founder Without Creation Evidence
Trigger:
```text
founder/co-founder title
but no creation/operations evidence
```
Effect:
```text
Initiative max = 55
```
Severity: MEDIUM

## ACT2-003 — Quantified Outcome Evidence
Trigger:
```text
number + recognized outcome context
```
Effect:
```text
increase evidence confidence
no automatic impact-score bonus
```
Severity: INFO

## ACT2-004 — Meaningful Outcome Evidence
Trigger:
```text
specific identifiable outcome supported by evidence
```
Effect:
```text
Impact & Outcomes anchor >=88
```
Severity: INFO

## ACT2-005 — Audience Size Guard
Always active.
Effect:
```text
audience/customer/follower/participant count must never directly map to impact score
```
Severity: INFO

## ACT2-006 — Sustained Commitment
Trigger:
```text
duration >=24 active months
```
Effect:
```text
duration anchor >=88
```
Severity: INFO

## ACT2-007 — Time Commitment Diminishing Returns
Trigger:
```text
hours/week >10
```
Effect:
```text
intensity capped at 95
no additional scoring benefit
```
Severity: INFO

## ACT2-008 — Weekly Hours Plausibility Warning
Trigger:
```text
sum of simultaneous extracurricular hours >70/week
```
Effect:
```text
warning only
```
Severity: HIGH  
Message must not accuse dishonesty.

## ACT2-009 — Family Responsibility Equivalence
Trigger:
```text
activity category == FAMILY_RESPONSIBILITY
```
Effect:
```text
evaluate with same ownership/impact/commitment framework
no category penalty
```
Severity: INFO

## ACT2-010 — Paid Work Equivalence
Trigger:
```text
activity category == PAID_WORK
```
Effect:
```text
evaluate with same framework
no category penalty
```
Severity: INFO

# ACTIVITY DESCRIPTION

## ACTDESC2-001 — Over Character Limit
Trigger:
```text
characters > configured maximum
```
Effect:
```text
Compliance/Conciseness reduced
```
Severity: CRITICAL

## ACTDESC2-002 — Low Character Use Is Not Automatic Weakness
Trigger:
```text
characters <50% of maximum
```
Effect:
```text
feedback only
no direct score penalty
```
Severity: INFO

## ACTDESC2-003 — Strong Action Near Start
Trigger:
```text
strong action in first 5 meaningful tokens
```
Effect:
```text
Action Clarity anchor = 95
```
Severity: INFO

## ACTDESC2-004 — Weak Participation Opening
Trigger:
```text
weak participation phrase dominates first clause
```
Effect:
```text
Action Clarity max = 55 unless later concrete action supports explicit override
```
Severity: LOW

## ACTDESC2-005 — Title/Description Redundancy
Trigger:
```text
normalized title-description token overlap >=60%
```
Effect:
```text
Redundancy Control reduced
```
Severity: LOW

# HONORS

## HON2-001 — Scope Unknown
Trigger:
```text
scope unavailable
```
Effect:
```text
Scope = N/A
confidence reduced
```
Severity: MEDIUM

## HON2-002 — Selectivity Unknown
Trigger:
```text
selection rate/participant evidence unavailable
```
Effect:
```text
Selectivity = N/A
redistribute weight
confidence reduced
```
Severity: LOW  
No default numerical selectivity score.

## HON2-003 — Award Title Prestige Guard
Always active.
Effect:
```text
award name cannot determine scope/selectivity
```
Severity: INFO

## HON2-004 — International Scope Evidence Missing
Trigger:
```text
scope == INTERNATIONAL
and countries/organizer/context absent
```
Effect:
```text
scope confidence LOW
scope may be capped pending evidence
```
Severity: MEDIUM

## HON2-005 — Major Relevance Is Metadata Only
Always active.
Effect:
```text
major relevance cannot alter Honor Distinction score
```
Severity: INFO

# ESSAY

## ESSAY2-001 — Word Limit Exceeded
Trigger: `word_count > max_words`
Effect:
```text
1–10  -> -15 compliance
11–25 -> -30
26–50 -> -50
51+   -> -80
```
Severity: CRITICAL

## ESSAY2-002 — Below Minimum Word Count
Use same tiered schedule.
Severity: CRITICAL

## ESSAY2-003 — Moderately Long Sentence
Trigger:
```text
31–40 words
```
Effect:
```text
-1 Sentence Control each
max -8
```
Severity: LOW

## ESSAY2-004 — Very Long Sentence
Trigger:
```text
41–50 words
```
Effect:
```text
-2 each
max -10
```
Severity: MEDIUM

## ESSAY2-005 — Extreme Sentence Length
Trigger:
```text
>50 words
```
Effect:
```text
-4 each
max -16
```
Severity: MEDIUM

## ESSAY2-006 — One-Paragraph Long Essay
Trigger:
```text
paragraph_count == 1 and word_count >=250
```
Effect:
```text
-20 Structural Balance
```
Severity: HIGH

## ESSAY2-007 — Dominant Paragraph
Trigger:
```text
paragraph_words / total_words >0.45
```
Effect:
```text
-10 Structural Balance
```
Severity: MEDIUM

## ESSAY2-008 — Excessively Short Paragraph Pattern
Trigger:
```text
count(paragraph_words <15) >=3
```
Effect:
```text
-5 Structural Balance
```
Severity: LOW

## ESSAY2-009 — Cliche Phrase
Trigger:
```text
versioned cliche dictionary match
```
Effect:
```text
-3 Style Hygiene each
max -15
```
Severity: LOW

## ESSAY2-010 — Filler Phrase
Trigger:
```text
versioned filler dictionary match
```
Effect:
```text
-2 each
max -12
```
Severity: LOW

## ESSAY2-011 — Repeated N-Gram
Trigger:
```text
same normalized 3+ word phrase occurs >=3 times excluding allowlist
```
Effect:
```text
-2 each qualifying phrase
max -12
```
Severity: MEDIUM

## ESSAY2-012 — Repeated Sentence Opening
Trigger:
```text
configured normalized opening pattern exceeds threshold
```
Effect:
```text
up to -8 Style Hygiene
```
Severity: LOW

## ESSAY2-013 — Reflection Marker Present
Trigger:
```text
reflection marker found
```
Effect:
```text
diagnostic signal only
no direct Essay Craft points
```
Severity: INFO

## ESSAY2-014 — Reflection Concentrated
Trigger:
```text
>=75% effective reflection markers in final quartile
and effective count >=2
```
Effect:
```text
Reflection Coverage = CONCENTRATED
no direct score effect
```
Severity: INFO

## ESSAY2-015 — Reflection Distributed
Trigger:
```text
markers in >=3 quartiles
```
Effect:
```text
Reflection Coverage = DISTRIBUTED
```
Severity: INFO

## ESSAY2-016 — Flesch Diagnostic Only
Always active when Flesch is calculated.
Effect:
```text
readability cannot alter Essay Craft score
```
Severity: INFO

## ESSAY2-017 — MATTR Adequate Sample
Trigger:
```text
token_count >=100
```
Effect:
```text
MATTR window 50
```
Severity: INFO

## ESSAY2-018 — MATTR Short Sample
Trigger:
```text
60 <= token_count <100
```
Effect:
```text
MATTR window 25
metric confidence LOW
```
Severity: INFO

## ESSAY2-019 — MATTR Insufficient Sample
Trigger:
```text
token_count <60
```
Effect:
```text
lexical variation = N/A
```
Severity: INFO

## ESSAY2-020 — Prompt Semantic Scoring Prohibited
Trigger:
```text
prompt exists and no deterministic prompt checklist exists
```
Effect:
```text
do not score semantic prompt relevance
```
Severity: INFO

# WRITING PATTERNS

## WPAT2-001 — Insufficient Text
Trigger:
```text
sample below configured minimum
```
Effect:
```text
Pattern Concentration = INSUFFICIENT_TEXT
```
Severity: HIGH

## WPAT2-002 — Sentence Rhythm Uniformity
Trigger:
```text
configured same-band / low-variance threshold exceeded
```
Effect: weighted pattern signal.
Severity: LOW or MEDIUM

## WPAT2-003 — Repeated Phrase Concentration
Trigger:
```text
normalized n-gram rate exceeds threshold
```
Effect: weighted pattern signal.
Severity: MEDIUM

## WPAT2-004 — Transition Overuse
Trigger:
```text
versioned transition-family density exceeds threshold
```
Effect: weighted pattern signal.
Severity: MEDIUM

## WPAT2-005 — Specific Detail Scarcity
Trigger:
```text
specific-detail density below threshold
```
Effect: weighted pattern signal.
Severity: LOW

## WPAT2-006 — Authorship Inference Prohibited
Always active.
Effect:
```text
never output AI probability or human/AI classification
```
Severity: CRITICAL product invariant

# LOR

## LOR2-001 — Relationship Context Missing
Trigger:
```text
role and duration absent
```
Effect:
```text
Relationship & Vantage Point <=30
```
Severity: HIGH

## LOR2-002 — Generic Praise Without Evidence
Trigger:
```text
generic praise sentence without concrete evidence in same/adjacent context
```
Effect:
```text
generic-praise overlay reduced
max total penalty -10
```
Severity: MEDIUM

## LOR2-003 — Concrete Anecdote
Trigger:
```text
distinct person/action/event/project/time evidence
```
Effect: counts toward Concrete Evidence.
Severity: INFO

## LOR2-004 — Duplicate Anecdote
Trigger:
```text
same normalized anecdote referenced repeatedly
```
Effect:
```text
count once
```
Severity: INFO

## LOR2-005 — Comparative Distinction
Trigger:
```text
recognized comparative statement
```
Effect: Comparative Distinction increases according to specificity.
Severity: INFO

## LOR2-006 — Explicit Strong Endorsement
Trigger:
```text
strong recommendation phrase in versioned dictionary
```
Effect: Endorsement Strength anchor increases.
Severity: INFO

## LOR2-007 — Contextualization Present
Trigger:
```text
letter explains school/course/recommender/student context relevant to evidence
```
Effect: Contextualization increases.
Severity: INFO

# COLLEGE EVALUATION

## COL2-001 — Admission Probability Prohibited
Always active.
Effect:
```text
do not compute/display exact admission probability
```
Severity: CRITICAL

## COL2-002 — Universal College Application Strength Deprecated
Always active for college-specific evaluation.
Effect:
```text
return component matrix instead of one primary overall chance/strength score
```
Severity: INFO

## COL2-003 — Missing International Admit Rate
Trigger:
```text
applicant international and international-specific rate unavailable
```
Effect:
```text
do not infer from overall rate
planning confidence max MEDIUM if overall rate used
```
Severity: INFO

## COL2-004 — Extreme Selectivity
Trigger:
```text
applicable admit rate <5%
```
Effect:
```text
Planning Category = HIGH_REACH
```
Severity: HIGH

## COL2-005 — Very High Selectivity
Trigger:
```text
5% <= applicable rate <10%
```
Effect:
```text
selectivity = VERY_HIGH
apply planning rules
```
Severity: INFO

## COL2-006 — Optional Testing No-Penalty
Trigger:
```text
test optional + applicant no score
```
Effect:
```text
testing excluded from Academic Alignment denominator
```
Severity: INFO

## COL2-007 — Required Material Missing
Trigger:
```text
required college material missing
```
Effect:
```text
Requirements = MISSING_REQUIRED
Planning Category cannot be LIKELY_ISH
```
Severity: CRITICAL

## COL2-008 — CDS Factor Priority Only
Trigger:
```text
CDS C7 importance available
```
Effect:
```text
use for explanation priority only
never claim official percentage weighting
```
Severity: INFO

## COL2-009 — Stale Critical College Data
Trigger:
```text
deadline/test policy/requirements/intl aid outside freshness threshold
```
Effect:
```text
Data Confidence max MEDIUM
```
Severity: HIGH

## COL2-010 — Multiple Critical Unknowns
Trigger:
```text
2+ critical target-college fields UNKNOWN
```
Effect:
```text
Data Confidence max LOW
Planning Category = INSUFFICIENT_DATA when rules depend on missing fields
```
Severity: HIGH

# FINANCIAL

## FIN2-001 — No International Need Aid
Trigger:
```text
international applicant requires aid
and college verified NO_NEED_BASED_AID
```
Effect:
```text
Financial Compatibility = HIGH_RISK or INCOMPATIBLE
depending verified budget gap / scholarship coverage
```
Severity: HIGH

## FIN2-002 — Need-Aware Aid Dependency
Trigger:
```text
international + need-aware + substantial aid required
```
Effect:
```text
Financial Risk = HIGH
```
No admission-probability penalty.
Severity: INFO

## FIN2-003 — Full Need Policy Verified
Trigger:
```text
intl need aid available + full demonstrated need commitment verified
```
Effect:
```text
pre-award Financial Compatibility may be POTENTIALLY_AFFORDABLE
```
Never infer actual net price.
Severity: INFO

## FIN2-004 — Actual Award Affordable
Trigger:
```text
actual award available
net_price <= family_budget
```
Effect:
```text
KNOWN_AFFORDABLE
```
Severity: INFO

## FIN2-005 — Actual Award Gap
Trigger:
```text
actual award available
net_price > family_budget
```
Effect:
```text
FUNDING_GAP/HIGH_RISK according to versioned tolerance
```
Severity: HIGH

## FIN2-006 — Stale Cost Data
Trigger:
```text
tuition/COA outside freshness threshold
```
Effect:
```text
financial confidence max MEDIUM
```
Severity: MEDIUM

# SCHOLARSHIPS

## SCH2-001 — Hard Eligibility Failure
Trigger:
```text
any mandatory criterion fails
```
Effect:
```text
NOT_ELIGIBLE
```
Severity: HIGH

## SCH2-002 — All Known Criteria Pass
Trigger:
```text
all mandatory criteria known and pass
```
Effect:
```text
ELIGIBLE
```
Severity: INFO

## SCH2-003 — Criterion Unknown
Trigger:
```text
one or more mandatory criteria unverified
and no known failure
```
Effect:
```text
POSSIBLY_ELIGIBLE
```
Severity: MEDIUM

## SCH2-004 — Scholarship Win Probability Prohibited
Always active.
Effect:
```text
never output probability of winning
```
Severity: CRITICAL

# APPLICATION AUDIT

## APP2-001 — Required Material Missing
Trigger:
```text
required material missing
```
Effect:
```text
status MISSING_REQUIRED
optional items excluded from denominator
```
Severity: CRITICAL

## APP2-002 — Optional Material Missing
Trigger:
```text
optional material missing
```
Effect:
```text
no completeness penalty
```
Severity: INFO

## APP2-003 — Deadline Passed
Trigger:
```text
evaluation_date > deadline and submitted == false
```
Effect:
```text
DEADLINE_PASSED
```
Severity: CRITICAL

# CONFIDENCE

## CONF2-001 — Official Source
Trigger:
```text
source = official university or official CDS
```
Effect:
```text
source authority = 100
```
Severity: INFO

## CONF2-002 — Federal Source
Trigger:
```text
source = IPEDS or College Scorecard
```
Effect:
```text
source authority = 95
```
Severity: INFO

## CONF2-003 — Official Common App
Trigger:
```text
source = official Common App
```
Effect:
```text
source authority = 90
```
Severity: INFO

## CONF2-004 — Critical Policy Stale
Trigger:
```text
critical policy outside freshness threshold
```
Effect:
```text
overall confidence max MEDIUM
```
Severity: HIGH

## CONF2-005 — Multiple Critical Unknowns
Trigger:
```text
2+ critical fields unknown
```
Effect:
```text
overall confidence max LOW
```
Severity: HIGH

# VERSIONING
All V2 IDs are new. Never repurpose V1 IDs.

Any change to trigger, threshold, evidence logic, score/status effect, severity, or confidence behavior requires:
1. rule-version bump;
2. rubric-version bump if result can change;
3. affected golden fixtures updated;
4. regression comparison;
5. changelog entry.
