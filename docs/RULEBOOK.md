# RULEBOOK.md

# Deterministic Rulebook

**Version:** 2.0.0  
**Rule ID format:** `<DOMAIN>-<NNN>`  
**Purpose:** Canonical specification for deterministic evaluation rules.

---

## 1. Rule Structure

Every rule must include:

```text
ID
Name
Domain
Category
Severity
Purpose
Trigger
Evidence
Score Effect
Feedback
Confidence
Version Introduced
```

Severity values:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFO
```

Confidence:

```text
HIGH
MEDIUM
LOW
```

---

# ESSAY RULES

## ESSAY-001 — Maximum Word Limit Exceeded

**Domain:** Essay  
**Category:** Compliance  
**Severity:** CRITICAL  
**Trigger:** `word_count > max_words`

Score effect:

```text
1–10 words over    -15 compliance
11–25              -30
26–50              -50
51+                -80
```

Feedback:

```text
Essay exceeds the {max_words}-word limit by {difference} words.
```

Evidence:

- word_count
- max_words
- difference

Confidence: HIGH

---

## ESSAY-002 — Below Minimum Word Count

Trigger:

```text
word_count < min_words
```

Use same tiered penalty schedule as ESSAY-001.

---

## ESSAY-003 — Very Long Sentence

**Severity:** MEDIUM

Trigger:

```text
sentence_words > 40
```

Evidence:

- sentence index
- word count
- sentence text excerpt

Score effect:

```text
-2 clarity per 41–50 word sentence
-4 clarity per >50 word sentence
```

Respect category caps from SCORING_SPEC.

---

## ESSAY-004 — Moderately Long Sentence

Trigger:

```text
31 <= sentence_words <= 40
```

Severity: LOW

Score effect:

```text
-1 clarity
```

---

## ESSAY-005 — Extreme Paragraph Dominance

Trigger:

```text
paragraph_word_count / total_words > 0.45
```

Severity: MEDIUM

Score effect:

```text
-10 structure
```

---

## ESSAY-006 — One-Paragraph Essay

Trigger:

```text
paragraph_count == 1
and word_count >= 250
```

Severity: HIGH

Score effect:

```text
-20 structure
```

---

## ESSAY-007 — Excessively Short Paragraph Pattern

Trigger:

```text
count(paragraph_words < 15) >= 3
```

Severity: LOW

Score effect:

```text
-5 structure
```

---

## ESSAY-008 — Cliché Phrase Detected

Trigger:

normalized phrase matches versioned cliché dictionary.

Severity: LOW

Score effect:

```text
-3 style_hygiene each
max -15
```

Feedback:

```text
Possible cliché detected: "{phrase}".
```

---

## ESSAY-009 — Filler Phrase Detected

Trigger:

normalized phrase matches filler dictionary.

Severity: LOW

Score effect:

```text
-2 style_hygiene each
max -12
```

---

## ESSAY-010 — Repeated 3+ Word Phrase

Trigger:

same normalized n-gram of length >=3 occurs >=3 times,
excluding stop-phrase allowlist.

Severity: MEDIUM

Score effect:

```text
-2 style_hygiene per qualifying phrase
max -12
```

---

## ESSAY-011 — Repeated Reflection Marker

Trigger:

same normalized reflection marker occurs >=3 times.

Severity: MEDIUM

Score effect:

Diminishing-return logic is applied to reflection score.

Additional feedback only; no duplicate direct penalty beyond SCORING_SPEC unless future version defines one.

---

## ESSAY-012 — Reflection Concentrated in Ending

Divide essay words into quartiles.

Trigger:

```text
>=75% effective reflection markers
occur in final quartile
and total effective markers >=2
```

Severity: LOW

Score effect:

```text
informational
```

Feedback:

```text
Most reflection indicators appear near the end of the essay.
```

---

## ESSAY-013 — No Reflection Signals

Trigger:

```text
effective_reflection_markers == 0
and word_count >= 250
```

Severity: MEDIUM

Score effect:

Handled through low Reflection Signals component.

---

## ESSAY-014 — Low Specificity Signal Density

Trigger:

```text
specificity_signals_per_100_words < 0.5
and word_count >= 250
```

Severity: MEDIUM

Score effect:

Handled by specificity component.

---

## ESSAY-015 — High Generic Phrase Density

Trigger:

generic phrase matches >= threshold per 100 words.

Initial threshold:

```text
>= 1.5 / 100 words
```

Severity: MEDIUM

Score effect:

```text
-10 voice indicators max
```

---

## ESSAY-016 — Repeated Sentence Opening

Normalize first 1–3 meaningful tokens.

Trigger:

```text
same opening appears in >=20% of sentences
and sentence_count >=10
```

Severity: LOW

Score effect:

```text
up to -8 voice
```

---

## ESSAY-017 — Healthy Paragraph Count

Trigger:

```text
3 <= paragraph_count <= 8
```

Severity: INFO

Score effect:

```text
+8 structure
```

---

## ESSAY-018 — Balanced Paragraph Distribution

Trigger:

no paragraph >35% of words and median paragraph length >=25.

Severity: INFO

Score effect:

```text
+6 structure
```

---

## ESSAY-019 — Dialogue Present

Trigger:

quoted dialogue-like pattern detected.

Severity: INFO

Score effect:

```text
+4 voice
```

maximum once.

---

## ESSAY-020 — Specific Numeric Evidence

Trigger:

one or more meaningful numeric tokens appear outside formatting artifacts.

Severity: INFO

Score effect:

Contributes to specificity signal count.

---

## ESSAY-021 — Date/Time Specificity Signal

Trigger:

date/time expression detected.

Severity: INFO

Score effect:

Contributes to specificity.

---

## ESSAY-022 — Named Project/Organization Signal

Trigger:

user-identified project/organization field appears in essay,
or safe deterministic proper-name pattern passes confidence threshold.

Severity: INFO

Score effect:

Contributes to specificity.

---

## ESSAY-023 — Excessive Short Sentences

Trigger:

```text
sentences_under_8_words / sentence_count > 0.35
```

Severity: LOW

Score effect:

```text
-10 sentence variety
```

---

## ESSAY-024 — Excessive Long Sentences

Trigger:

```text
sentences_over_35_words / sentence_count > 0.25
```

Severity: MEDIUM

Score effect:

```text
-15 sentence variety
```

---

## ESSAY-025 — Low Sentence-Length Diversity

Trigger:

```text
>=60% of sentences in same configured length band
```

Severity: LOW

Score effect:

```text
-15 sentence variety
```

---

## ESSAY-026 — Extreme Readability Difficulty

Trigger:

```text
Flesch Reading Ease < 20
```

Severity: MEDIUM

Score effect:

```text
-12 clarity
```

---

## ESSAY-027 — Difficult Readability

Trigger:

```text
20 <= Flesch Reading Ease < 35
```

Severity: LOW

Score effect:

```text
-8 clarity
```

---

## ESSAY-028 — Moderately Difficult Readability

Trigger:

```text
35 <= Flesch Reading Ease < 50
```

Severity: LOW

Score effect:

```text
-4 clarity
```

---

## ESSAY-029 — Excessive Passive Pattern

Trigger:

configured deterministic passive-pattern ratio exceeds threshold.

Initial threshold:

```text
>20% of sentences
```

Severity: LOW

Score effect:

```text
up to -8 clarity
```

This is a heuristic and must be labeled as such.

---

## ESSAY-030 — Essay Draft Improvement

Used only in `/essay compare`.

Trigger:

new draft component score exceeds old by >=5 points.

Severity: INFO

Feedback:

```text
{component} improved by {delta} points.
```

No score effect.

---

# ACTIVITY RULES

## ACT-001 — Position/Description Redundancy

Compare normalized title tokens with first 30 characters of description.

Trigger:

```text
token_overlap >= 0.60
```

Severity: LOW

Score effect:

handled by redundancy component.

---

## ACT-002 — Strong Action Verb Near Start

Trigger:

strong-action dictionary match in first 5 meaningful tokens.

Severity: INFO

Score effect:

Action Clarity anchor = 95.

---

## ACT-003 — Weak Participation Phrase Dominant

Examples:

```text
participated in
helped with
was involved in
was responsible for
```

Trigger:

weak phrase appears before a strong action and dominates first clause.

Severity: LOW

Score effect:

Action Clarity maximum = 55 unless another concrete action exists.

---

## ACT-004 — Quantified Impact Present

Trigger:

description includes a number plus recognized impact context.

Examples:

- users
- members
- customers
- revenue
- funds raised
- participants
- downloads
- events

Severity: INFO

Score effect:

Impact Evidence may reach 95.

---

## ACT-005 — Generic Activity Description

Trigger:

no strong action, no responsibility phrase, no measurable impact, no specific output.

Severity: MEDIUM

Score effect:

Impact Evidence maximum = 52.

---

## ACT-006 — Founder Without Responsibility Evidence

Trigger:

position contains founder/co-founder,
but description lacks operational or creation evidence.

Severity: MEDIUM

Score effect:

```text
leadership max 10
initiative max 8
```

---

## ACT-007 — Sustained Multi-Year Activity

Trigger:

```text
duration_months >=24
```

Severity: INFO

Score effect:

duration determined by scoring table.

---

## ACT-008 — Implausible Total Weekly Hours

Trigger:

sum of simultaneous self-reported extracurricular hours >70/week.

Severity: HIGH

Score effect:

none automatically.

Feedback:

```text
Reported weekly commitments may overlap or exceed a plausible total. Review the entries for accuracy.
```

Do not accuse user of dishonesty.

---

## ACT-009 — Description Over Character Limit

Trigger:

description character count > configured field limit.

Severity: CRITICAL

Score effect:

character efficiency anchor = 20.

---

## ACT-010 — Low Character Utilization

Trigger:

character use <50%.

Severity: INFO

Score effect:

character efficiency anchor = 55.

---

## ACT-011 — Clear Advancement

Trigger:

explicit progression from lower to higher responsibility levels entered in structured fields.

Severity: INFO

Score effect:

progression = 4 or 5 depending number of levels.

---

## ACT-012 — Activity Stuffing Guard

Trigger:

activity #5 onward materially lowers average but count is high.

Severity: INFO

Score effect:

none.

Portfolio uses top-weighted system and does not reward activity count alone.

---

# HONOR RULES

## HON-001 — Award Scope Unknown

Trigger:

scope missing.

Severity: MEDIUM

Score effect:

scope cannot be scored; overall honor confidence reduced.

---

## HON-002 — Selectivity Unknown

Trigger:

participant count and selection rate missing.

Severity: LOW

Score effect:

selectivity default = 8/25.

---

## HON-003 — Award Title Prestige Guard

Always active.

Rule:

```text
award title must never directly determine scope or selectivity
```

Severity: INFO

No direct score.

---

## HON-004 — International Scope Claimed Without Context

Trigger:

scope = international and countries/organizer/context fields all empty.

Severity: MEDIUM

Score effect:

scope maximum = national-equivalent 27 until context supplied.

---

# ACADEMIC RULES

## ACAD-001 — Missing Grading Scale

Trigger:

grading system not recognized and scale bounds missing.

Severity: HIGH

Effect:

performance score unavailable.

---

## ACAD-002 — Forced GPA Conversion Prohibited

Always active for non-US grading systems.

Rule:

Do not automatically convert percentage/IB/A-Level results to US 4.0 GPA.

Severity: INFO

---

## ACAD-003 — Positive Academic Trend

Trigger:

slope >= +1 point per semester.

Severity: INFO

Score effect:

mapped by SCORING_SPEC.

---

## ACAD-004 — Negative Academic Trend

Trigger:

slope <= -1 point per semester.

Severity: MEDIUM

Score effect:

mapped by trend table.

---

## ACAD-005 — No Advanced Courses Available

Trigger:

school reports zero applicable advanced courses.

Severity: INFO

Score effect:

do not penalize advanced utilization for nonavailability.

---

## ACAD-006 — Major Preparation Gap

Trigger:

declared major has configured prerequisite group and applicant lacks core prerequisite.

Severity: HIGH

Score effect:

major preparation may fall to 1/10 within rigor.

---

# TEST RULES

## TEST-001 — Required Test Missing

Trigger:

college test policy = REQUIRED and no valid score.

Severity: CRITICAL

Effect:

Requirements Fit = incomplete.

---

## TEST-002 — Optional Test Missing

Trigger:

college test policy = OPTIONAL and no valid score.

Severity: INFO

Effect:

testing excluded; no penalty.

---

## TEST-003 — Test Blind College

Trigger:

college test policy in BLIND/NOT_ACCEPTED.

Severity: INFO

Effect:

testing ignored entirely.

---

## TEST-004 — Score Above Published 75th

Trigger:

applicant score > P75.

Severity: INFO

Effect:

test alignment 92–100 by interpolation.

---

## TEST-005 — Score Below Published 25th

Trigger:

applicant score < P25.

Severity: INFO

Effect:

test alignment <60 depending distance.

---

# LOR RULES

## LOR-001 — Relationship Context Missing

Trigger:

no relationship role or duration indicators.

Severity: HIGH

Effect:

Relationship Context <=30.

---

## LOR-002 — Generic Praise Without Evidence

Trigger:

generic praise term exists in sentence with no concrete evidence signal.

Severity: MEDIUM

Effect:

Generic Praise Control reduced.

---

## LOR-003 — Comparative Evidence Present

Trigger:

recognized comparison pattern found.

Examples:

```text
top 5%
among the strongest
one of the best
in my X years
```

Severity: INFO

Effect:

comparative component increased according to count and diversity.

---

## LOR-004 — Concrete Example Detected

Trigger:

sentence/paragraph contains a person action + event/project/time-specific evidence.

Severity: INFO

Effect:

counts toward Specific Evidence.

---

# COLLEGE RULES

## COL-001 — Stale Critical Data

Trigger:

critical college fact last verified before configured freshness threshold.

Severity: HIGH

Effect:

college data confidence capped at MEDIUM.

Critical fields:

- application deadline;
- testing policy;
- essay requirement;
- recommendation requirement;
- international aid policy.

---

## COL-002 — Missing International Admit Rate

Trigger:

applicant is international and college-specific international admit rate unavailable.

Severity: INFO

Effect:

do not infer from overall rate.

---

## COL-003 — Ultra-Selective Safety Guard

Trigger:

overall admit rate <10%.

Severity: HIGH

Effect:

planning category cannot become LIKELY_ISH.

---

## COL-004 — Extreme Selectivity

Trigger:

admit rate <5%.

Severity: INFO

Effect:

planning category defaults HIGH_REACH regardless of high academic alignment.

---

## COL-005 — Test Optional No-Penalty Guard

Trigger:

test optional and applicant score absent.

Effect:

testing removed from denominator.

---

## COL-006 — Requirement Missing

Trigger:

any required application material status = missing.

Severity: CRITICAL

Effect:

Requirements Fit = INCOMPLETE.

---

## COL-007 — College-Specific CDS Weight

Trigger:

CDS factor available.

Effect:

apply internal mapping:

```text
VERY_IMPORTANT 1.00
IMPORTANT      0.70
CONSIDERED     0.35
NOT_CONSIDERED 0.00
```

Metadata must state these are internal weights.

---

## COL-008 — Unknown CDS Factor

Trigger:

CDS importance unavailable.

Effect:

use default product weight only if explicitly configured;
otherwise exclude and reduce confidence.

---

# FINANCIAL RULES

## FIN-001 — Need-Based Aid Unavailable

Trigger:

international applicant requires substantial aid and college has no international need-based aid.

Severity: HIGH

Effect:

Financial Fit = POOR/INCOMPATIBLE.

---

## FIN-002 — Need-Aware International Applicant

Trigger:

international + need-aware + applicant indicates substantial aid need.

Severity: INFO

Effect:

Financial Risk = HIGH.

Do not transform this into a precise admission probability penalty.

---

## FIN-003 — Budget Exceeds Estimated Net Requirement

Trigger:

reliable estimated required family contribution <= user max budget.

Severity: INFO

Effect:

Financial Fit may be STRONG.

---

## FIN-004 — Cost Data Stale

Trigger:

COA/tuition data outside freshness threshold.

Severity: MEDIUM

Effect:

Financial confidence capped at MEDIUM.

---

# APPLICATION COMPLETENESS RULES

## APP-001 — Required Material Missing

Trigger:

college requirement = required,
user status = missing.

Severity: CRITICAL

Effect:

application completeness reduced and critical priority created.

---

## APP-002 — Optional Material Missing

Trigger:

college requirement = optional,
user status = missing.

Severity: INFO

Effect:

no completeness penalty.

---

## APP-003 — Material Present But Not Evaluated

Trigger:

material exists but no evaluation version is stored.

Severity: LOW

Effect:

completeness remains complete;
quality status = NOT_EVALUATED.

---

## APP-004 — Deadline Passed

Trigger:

current evaluation date > deadline and submitted = false.

Severity: CRITICAL

Effect:

application status = DEADLINE_PASSED.

Date must be explicitly supplied to deterministic evaluation.

---

# DATA QUALITY RULES

## DATA-001 — Missing Source URL

Trigger:

verified college fact has no source URL.

Severity: HIGH

Effect:

record cannot receive VERIFIED status.

---

## DATA-002 — Invalid SAT Percentile Order

Trigger:

```text
P25 > P50 or P50 > P75
```

Severity: CRITICAL

Effect:

reject import row.

---

## DATA-003 — Invalid Admit Rate

Trigger:

rate <0 or >1.

Severity: CRITICAL

Effect:

reject import row.

---

## DATA-004 — Unknown Enum Value

Trigger:

source value cannot map to a known enum.

Severity: HIGH

Effect:

store UNKNOWN in staging and require review.

---

# PRIVACY RULES

## PRIV-001 — Temporary Upload Cleanup

Trigger:

analysis completes or fails.

Effect:

delete temporary document and containing temporary directory.

Severity: CRITICAL operational requirement.

---

## PRIV-002 — Sensitive Content Logging Prohibited

Always active.

Logs must not contain:

- essay text;
- LOR text;
- transcript contents;
- detailed family finances;
- raw upload URLs or signed storage URLs.

---

## PRIV-003 — Explicit Save Required

Trigger:

user uploads essay/LOR/transcript.

Effect:

do not persist raw file unless user explicitly requested save.

---

# RULE PRIORITIZATION

Priority ranking:

```text
CRITICAL > HIGH > MEDIUM > LOW > INFO
```

Within same severity:

1. larger score impact;
2. higher confidence;
3. earlier textual position where relevant;
4. lower rule ID as deterministic tie breaker.

Default web summary output:

```text
top 5 actionable rules
```

Full report may include all triggered rules.

---

# RULE CHANGE POLICY

Any change to:

- trigger condition;
- score effect;
- evidence logic;
- severity;
- threshold;

requires:

1. rule version change;
2. affected golden tests updated;
3. changelog entry;
4. regression comparison.

Rule IDs must never be reused for different meanings.


---

# WEB OPERATIONAL RULES

## WEB-001 — Anonymous Analysis Persistence Guard

Trigger:

```text
request is anonymous
```

Effect:

```text
raw essay/LOR/profile content must not be persisted
```

Severity: CRITICAL operational rule.

---

## WEB-002 — Authenticated Ownership Guard

Trigger:

```text
request accesses user-owned resource
```

Effect:

Resource owner must match verified authentication subject through internal user mapping.

Client-provided user IDs must not grant authorization.

Severity: CRITICAL.

---

## WEB-003 — Direct Upload Size Guard

Trigger:

```text
upload > 4 MB
```

Effect:

Reject before parser execution.

Severity: HIGH.

---

## WEB-004 — Public Cache Guard

Trigger:

private profile/evaluation/report response.

Effect:

```text
Cache-Control: private, no-store
```

Severity: HIGH.

---

## WEB-005 — Raw Text Save Requires Explicit Opt-In

Trigger:

essay/LOR analysis with no explicit `save_raw_text=true`.

Effect:

Raw text must not be persisted.

Severity: CRITICAL operational rule.
