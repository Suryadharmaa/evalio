# CODEX_PROMPT_SCORING_V2.md

Implement **Evalio Scoring Engine V2** from the new canonical specifications.

Before coding, read:

- `docs/PRD.md`
- `docs/TECHNICAL_DESIGN.md`
- `docs/DATA_SPEC.md`
- `docs/API_SPEC.md`
- `docs/SECURITY.md`
- `docs/TEST_PLAN.md`
- `docs/TOOLS_SPEC.md`
- current `docs/SCORING_SPEC.md`
- current `docs/RULEBOOK.md`
- `docs/SCORING_SPEC_V2.md`
- `docs/RULEBOOK_V2.md`
- `docs/SCORING_MIGRATION_V1_TO_V2.md`

For V2 scoring behavior, the three V2 documents are authoritative.

Do NOT delete, mutate, or silently reinterpret V1 stored evaluations.

Goal:

```text
V1 remains reproducible
V2 becomes the new deterministic engine for new evaluations after validation
```

## Hard constraints

- no LLM
- no AI API
- no local AI model
- no machine learning
- no embeddings
- no vector database
- no admission-probability model
- no scholarship win probability
- no AI-authorship probability
- no forced international GPA conversion
- no frontend authoritative scoring formulas
- no invented college data
- no silent V1 backfill
- no unrelated frontend redesign

Use:

```text
engine_version = 2.0.0
```

Use the domain rubric versions defined in the migration spec.

# PHASE 0 — AUDIT FIRST

Before changing code, inspect:

- scoring engines/services
- rule registry
- domain/Pydantic models
- evaluation repository/storage
- SQLAlchemy models
- API response schemas
- frontend result assumptions
- test fixtures
- golden tests
- feature/version switches
- existing methodology rendering

Write a concise implementation map internally and continue unless technically blocked.

Do not invent duplicate business logic.

# PHASE 1 — SHARED V2 FRAMEWORK

Implement/reuse:

- engine-version registry
- rubric-version registry
- V2 rule registry
- unique rule-ID validation
- score clamping
- internal/display rounding
- `N/A` behavior
- weighted denominator redistribution
- confidence object `{score, band}`
- status-only evaluation result shape
- deterministic result ordering
- V1/V2 regression comparison helper

Keep V1 IDs and meanings unchanged.

# PHASE 2 — ACADEMICS / COURSEWORK / TESTING

Implement exactly from `SCORING_SPEC_V2.md`:

- Academic Achievement V2
- native-scale handling
- rank corroboration
- Theil–Sen trend
- Academic Strength V2
- Course Rigor V2
- school opportunity guardrails
- Major Preparation status
- College Test Alignment V2

Required guards:

```text
non-US grades -> no forced 4.0 conversion
no AP/IB offered -> no advanced-course penalty
rank unavailable -> no penalty
test median absent -> never infer P50
OPTIONAL + no score -> N/A
REQUIRED + no score -> REQUIREMENT_INCOMPLETE
BLIND -> testing excluded
PROGRAM_DEPENDENT unresolved -> TEST_POLICY_UNKNOWN
```

Add golden and threshold-boundary tests before proceeding.

# PHASE 3 — ACTIVITIES / DESCRIPTIONS / HONORS

Implement:

- Activity Strength V2
- Responsibility & Ownership
- Impact & Outcomes
- Initiative
- Sustained Commitment
- Growth / Progression
- existing top-weighted Activity Portfolio aggregation
- Activity Description Craft V2
- Honor Distinction V2

Required behavior:

- audience size never directly maps to impact score
- founder title alone cannot produce a high Initiative score
- title alone caps Responsibility
- quantitative outcome increases evidence confidence, not impact automatically
- paid work has no category penalty
- family responsibilities have no category penalty
- hours/week has diminishing returns and no score gain beyond configured cap
- >70 simultaneous hours = warning only
- unknown honor selectivity = N/A
- award-title prestige must never determine selectivity/scope
- major relevance does not affect Honor Distinction

# PHASE 4 — ESSAY / WRITING PATTERNS / LOR

Implement:

## Essay Craft V2
Components:

```text
Compliance
Sentence Control
Structural Balance
Specificity Signals
Repetition & Style Hygiene
```

Diagnostic-only signals:

```text
Reflection Coverage
MATTR
Readability
Sentence Rhythm
Personal Anchoring
```

Required:

- reflection marker count does NOT add Essay Craft points
- Flesch does NOT alter Essay Craft
- "Voice Indicators" removed from the numeric craft formula
- MATTR uses window 50 for >=100 tokens
- MATTR window 25 for 60–99 tokens with LOW confidence
- <60 tokens -> lexical variation N/A
- no semantic prompt-fit scoring unless a deterministic prompt checklist exists

## Writing Pattern Checker V2
Return only:

```text
LOW
MODERATE
HIGH
INSUFFICIENT_TEXT
```

Mandatory disclaimer:

> This tool identifies measurable writing patterns. It cannot determine who or what wrote the text.

Never output:
```text
AI %
AI-written
human-written
authenticity %
```

## LOR Evidence V2
Implement all V2 dimensions and generic-praise overlay.

Required:

- repeated same anecdote counts once
- comparison must be explicitly evidenced
- relationship/vantage point separate from praise
- no claim that the letter guarantees or predicts admission

# PHASE 5 — COLLEGE / FINANCIAL / SCHOLARSHIP / APPLICATION AUDIT

Implement:

- Academic Alignment V2
- Selectivity Risk
- Planning Category V2
- CDS factor importance as explanation-priority metadata
- Financial Compatibility status
- Scholarship Eligibility status
- Required Completion %
- Data Confidence V2

Required:

## College
Do not produce one universal admission/chance score as the primary college-specific output.

Return component matrix:

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

Never infer international admit rate from overall admit rate.

If only overall rate exists for an international applicant:
- it may describe institution-level selectivity;
- planning confidence max MEDIUM;
- expose note that international-specific rate is unavailable.

## CDS
If C7 importance exists, show:

```text
VERY_IMPORTANT
IMPORTANT
CONSIDERED
NOT_CONSIDERED
UNKNOWN
```

Do not present internal explanation-priority mapping as an official admissions percentage.

## Financial
Pre-award result is categorical:

```text
KNOWN_AFFORDABLE
POTENTIALLY_AFFORDABLE
FUNDING_GAP
HIGH_RISK
INCOMPATIBLE
INSUFFICIENT_DATA
```

Do not invent net price.

With an actual award:
```text
net_price = COA - grants - scholarships
annual_gap = net_price - family_budget
```

Do NOT subtract loans or work-study as grants.

## Scholarships
Return:

```text
ELIGIBLE
POSSIBLY_ELIGIBLE
NOT_ELIGIBLE
INSUFFICIENT_DATA
```

Never probability of winning.

## Application Audit
Only required items enter completeness denominator.
Optional missing material cannot reduce required-completion %.

# PHASE 6 — STORAGE / API

Preserve V1.

If current storage cannot represent V2 status-only outputs, create the smallest backward-compatible Alembic migration.

Preferred semantics:

```text
overall_score nullable
status nullable
confidence_score nullable
confidence_band nullable
signals_json nullable
```

Do not create duplicate evaluation tables if the current schema already supports equivalent data.

Every V2 response must return:

```text
request_id
engine_version
rubric_version
confidence
```

Frontend/API code must not assume every evaluation has `overall_score`.

# PHASE 7 — FRONTEND COMPATIBILITY ONLY

Update only result language and rendering required by V2.

Required terminology:

```text
Mechanical Essay Score -> Essay Craft Score
AI Risk / AI probability -> Pattern Concentration
```

College-specific evaluator:
- remove probability-like headline;
- use V2 component matrix;
- show evidence/confidence/source provenance.

Financial:
- categorical pre-award compatibility.

Scholarship:
- eligibility status, no win score.

Do not redesign unrelated pages.

# PHASE 8 — GOLDEN / BOUNDARY / REGRESSION TESTS

Implement every fixture from `SCORING_MIGRATION_V1_TO_V2.md`.

Every numerical threshold must be tested at:

```text
threshold - epsilon
threshold
threshold + epsilon
```

Required regression output:

```text
fixture_id
domain
v1_score_or_status
v2_score_or_status
delta_or_change
expected_reason
unexpected_change
```

Large expected V1/V2 differences are acceptable only if explicitly explained by V2 semantics.

Add repeatability tests proving:

```text
same input
same rubric version
same data snapshot
same evaluation date
=> same normalized output
```

Ignore only request IDs/timestamps/runtime telemetry.

# VERSION / ROLLOUT SAFETY

Add or preserve version selection such as:

```text
SCORING_ENGINE_VERSION=v1|v2
```

Historical V1 reports remain V1.

Explicit re-evaluation creates a new V2 record.

Do NOT automatically re-score old results.

Keep a V1 rollback path until production acceptance.

# REQUIRED CHECKS

Run all relevant:

```text
pytest
ruff
mypy
frontend tests
frontend typecheck
frontend lint
production build
database migration tests if schema changed
```

Inspect git diff.

# FINAL REPORT

Return:

1. current scoring architecture discovered;
2. files changed;
3. migrations created;
4. V2 engines implemented;
5. V1 compatibility status;
6. golden fixtures added;
7. threshold-boundary tests added;
8. regression summary;
9. API changes;
10. frontend result-language changes;
11. exact test/typecheck/build results;
12. unresolved ambiguities;
13. exact environment/config switch for V1 vs V2.

Do not claim implementation for any phase that was not actually completed.

If the full implementation is too large for one safe change, stop only at a clean phase boundary with passing tests and explicitly state which next phase remains. Do not leave a half-migrated engine.
