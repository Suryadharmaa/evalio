# API_SPEC.md

# Web API Specification

**Version:** 1.0.0  
**Base path:** `/api/v1`  
**Backend:** FastAPI  
**Content:** JSON except multipart uploads

---

## 1. Response Envelope

Success:

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid",
    "engine_version": "2.0.0"
  }
}
```

Error:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Invalid request.",
    "fields": {}
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

---

## 2. Authentication

Protected endpoints:

```text
Authorization: Bearer <Supabase access token>
```

Backend verifies token.

Never accept user identity from request body.

---

## 3. Public Endpoints

### GET `/health`

Returns:

```json
{
  "status": "ok",
  "engine_version": "2.0.0"
}
```

### GET `/health/ready`

Returns `200 ready` only when the database is reachable and `alembic_version` matches the application's expected schema revision; otherwise returns `503 not_ready`. This endpoint is used by deployment smoke checks and is never cached.

No sensitive infrastructure details.

### GET `/methodology`

Returns public current rubric/version metadata.

### GET `/colleges`

Query:

```text
q
state
test_policy
need_policy
page
page_size
```

Max page size:

```text
50
```

### GET `/colleges/{slug}`

Returns public college data + source/freshness metadata.

---

## 4. Essay Analysis

### POST `/evaluations/essay`

May be anonymous.

JSON request:

```json
{
  "essay_type": "COMMON_APP",
  "text": "...",
  "min_words": 250,
  "word_limit": 650,
  "prompt_text": null,
  "save": false
}
```

Rules:

- anonymous `save` must be false;
- max text 100,000 chars;
- authenticated save persists only if explicitly true.

Response:

```json
{
  "data": {
    "evaluation": {
      "overall_score": 81,
      "label": "Strong",
      "confidence": "HIGH",
      "components": {
        "compliance": 100,
        "clarity": 84,
        "structure": 81,
        "specificity": 76,
        "reflection": 83,
        "voice": 79,
        "sentence_variety": 86,
        "style_hygiene": 72
      },
      "metrics": {},
      "issues": []
    }
  }
}
```

### POST `/evaluations/essay/upload`

Multipart:

```text
file
essay_type
min_words
word_limit
save
```

Max direct upload:

```text
4 MB
```

### POST `/evaluations/writing-patterns`

May be anonymous. Raw input text is processed for the request and is not persisted.

JSON request:

```json
{
  "text": "..."
}
```

Returns a versioned `LOW`, `MODERATE`, or `HIGH` writing-pattern risk plus 25
deterministic signal records. Every signal includes its metric, observed value,
threshold, status, evidence where applicable, and explanation. Sample-dependent
signals return `INSUFFICIENT_DATA` when the input is too short.

This endpoint does not return an AI probability or human/AI authorship label.

### POST `/essay-ideas/build`

May be anonymous. Accepts bounded arrays of user-provided moments, experiences,
activities, values, challenges, turning points, people or places, and lessons or
changes. At least three grounded combinations must be possible.

Returns three to eight deterministic brainstorming directions. Each direction
contains the source moment, tension, core value, change, reflection direction,
possible prompt fit, and questions to explore. It never returns finished essay
paragraphs and does not persist the submitted details.

---

## 5. Activity Description

### POST `/evaluations/activity-description`

Public.

Request:

```json
{
  "position_title": "Founder",
  "organization": "Example",
  "description": "...",
  "character_limit": 150
}
```

Returns:

- character efficiency;
- action clarity;
- impact evidence;
- specificity;
- redundancy;
- triggered rules.

---

## 6. Authenticated Profile

### GET `/me`

Returns basic internal account state.

### GET `/profiles`

### POST `/profiles`

Request:

```json
{
  "profile_name": "2027 US Applications",
  "applicant_type": "INTERNATIONAL",
  "country_code": "ID",
  "graduation_year": 2027,
  "curriculum_type": "INDONESIA_KURIKULUM_MERDEKA",
  "intended_major": "Finance"
}
```

### GET `/profiles/{profile_id}`

Owner only.

### PATCH `/profiles/{profile_id}`

Owner only.

### DELETE `/profiles/{profile_id}`

Owner only.

---

## 7. Academics

### GET `/profiles/{profile_id}/academic-terms`

### PUT `/profiles/{profile_id}/academic-terms`

Bulk replace/upsert structured terms.

### GET `/profiles/{profile_id}/courses`

### PUT `/profiles/{profile_id}/courses`

Bulk replace/upsert courses.

### POST `/profiles/{profile_id}/evaluate/academic`

Returns deterministic academic evaluation.

### GET `/profiles/{profile_id}/school-context`

### PUT `/profiles/{profile_id}/school-context`

Owner-scoped school opportunity context used by rigor evaluation.

---

## 8. Tests

### GET `/profiles/{profile_id}/tests`

### POST `/profiles/{profile_id}/tests`

### PATCH `/profiles/{profile_id}/tests/{test_id}`

### DELETE `/profiles/{profile_id}/tests/{test_id}`

---

## 9. Activities

### GET `/profiles/{profile_id}/activities`

### POST `/profiles/{profile_id}/activities`

### PATCH `/profiles/{profile_id}/activities/{activity_id}`

### DELETE `/profiles/{profile_id}/activities/{activity_id}`

### POST `/profiles/{profile_id}/evaluate/activities`

Returns individual + portfolio results.

---

## 10. Honors

Equivalent owner-scoped CRUD:

```text
/profiles/{profile_id}/honors
```

and:

```text
POST /profiles/{profile_id}/evaluate/honors
```

---

## 11. Saved Essays

Protected:

```text
GET    /profiles/{profile_id}/essays
POST   /profiles/{profile_id}/essays
GET    /profiles/{profile_id}/essays/{essay_id}
DELETE /profiles/{profile_id}/essays/{essay_id}
```

Raw text only exists if explicit save.

The detail response contains `{ essay, evaluation }`; evaluation includes persisted components, metrics, and triggered-rule evidence.

Saved history items include their latest evaluation ID, display score, and confidence when available.

### Saved Recommendations

```text
GET    /profiles/{profile_id}/recommendations
POST   /profiles/{profile_id}/recommendations
DELETE /profiles/{profile_id}/recommendations/{recommendation_id}
```

Raw recommendation text is stored only with explicit opt-in.

---

## 12. Essay Compare

### POST `/evaluations/essay/compare`

Request can contain:

```json
{
  "left_evaluation_id": "...",
  "right_evaluation_id": "..."
}
```

Authenticated saved results only.

Saved comparison IDs must be distinct. Anonymous compare accepts two full essay inputs and does not persist them.

### POST `/lor/build`

Public, non-persistent deterministic framework builder. It accepts recommender role,
student name, relationship context/duration, qualities, specific examples, optional
academic/community/comparative evidence, and an explicit endorsement strength.

It returns five editable framework sections. Every evidence or sentence-shell item
includes `source_fields`; writing prompts contain visible placeholders and do not
assert facts. No completed recommendation letter or invented claim is returned.

---

## 13. College Evaluation

### POST `/profiles/{profile_id}/colleges/{college_id}/evaluate`

Request:

```json
{
  "evaluation_date": "2026-09-09"
}
```

Response:

```json
{
  "college": { "id": "...", "slug": "bowdoin-college", "name": "Bowdoin College" },
  "academic_alignment": 88,
  "application_strength": 84,
  "course_rigor": 91,
  "components": {
    "academics": 88,
    "activities": 84,
    "honors": 76,
    "testing": null
  },
  "selectivity_risk": "VERY_HIGH",
  "requirements_fit": "COMPATIBLE",
  "financial_fit": "STRONG",
  "planning_category": "HIGH_REACH",
  "confidence": "HIGH",
  "confidence_score": 91,
  "college_data_cycles": {
    "admissions": "2026-27",
    "requirements": "2026-27",
    "financial_aid": "2026-27",
    "cds": "2026-27"
  },
  "source_freshness": "CURRENT",
  "reasons": [],
  "triggered_rules": ["COL-007"]
}
```

Application Strength uses available profile signals weighted by the college's latest mapped CDS factors. Unknown factors are excluded and reduce confidence. No acceptance probability field.

Missing components are returned as absent/`null` and displayed as `N/A`; they are
not converted to zero. College data cycles and aggregate critical-source freshness
must remain visible to the user.

---

## 14. Target Colleges

```text
GET    /profiles/{profile_id}/targets
POST   /profiles/{profile_id}/targets
PATCH  /profiles/{profile_id}/targets/{target_id}
DELETE /profiles/{profile_id}/targets/{target_id}
```

---

## 15. Application Audit

### GET `/profiles/{profile_id}/colleges/{college_id}/materials`

### PUT `/profiles/{profile_id}/colleges/{college_id}/materials`

Reads or replaces the owner-scoped material checklist.

### POST `/profiles/{profile_id}/colleges/{college_id}/audit`

Returns:

- checklist;
- missing required;
- optional;
- deadlines;
- critical issues;
- readiness;
- priorities.

---

## 16. Reports

### GET `/profiles/{profile_id}/reports`

Lists up to 100 owner-scoped saved reports, newest first.

### POST `/profiles/{profile_id}/reports`

Creates an `APPLICATION_READINESS` report. Sections are restricted to a bounded profile name and at most 20 latest evaluation summaries; arbitrary or raw essay/recommendation text is rejected.

### GET `/reports/{report_id}`

Owner only.

### DELETE `/reports/{report_id}`

Owner only.

Printable web page consumes report JSON.

---

## 17. Privacy

### GET `/account/export`

Returns downloadable JSON or initiates generated export.

### DELETE `/account`

Requires explicit confirmation payload:

```json
{
  "confirm": "DELETE"
}
```

Backend verifies session before deletion.

---

## 18. Admin API

Prefix:

```text
/api/v1/admin
```

Required server-side admin authorization.

Endpoints:

```text
POST /imports
GET  /imports/{id}
POST /imports/{id}/validate
POST /imports/{id}/approve
POST /imports/{id}/promote
GET  /sources/stale
GET  /rules
GET  /system
```

Normal users must receive 403.

---

## 19. Pagination

List responses:

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 123
  }
}
```

---

## 20. Idempotency

State-creating admin import/promote endpoints should support an idempotency key.

Normal profile POST operations may reject accidental duplicates with 409 where appropriate.

---

## 21. Caching

Public college GET:

```text
cacheable
```

Private/profile endpoints:

```text
Cache-Control: private, no-store
```

Essay/LOR analysis responses:

```text
no-store
```

---

## 22. Versioning

Breaking API changes require:

```text
/api/v2
```

Scoring changes do not require API version change when response schema is compatible; they require rubric/engine version increments.
## GPA calculator

`POST /api/v1/calculators/gpa` performs a stateless, versioned calculation. `US_COURSES` accepts letter grades, course levels, credits, and an explicit weighting method; it returns credit-weighted unweighted and weighted GPAs. `INTERNATIONAL_RAW` accepts a curriculum name, custom scale, and weighted course or term values; it returns the academic average on that original scale with `conversion: NOT_APPLIED`. Responses include exact formulas and a row-level breakdown. Inputs are not persisted.

## Coursework evaluator

`POST /api/v1/evaluations/coursework` evaluates course rigor against school opportunities supplied in the request. It returns the versioned overall score plus challenge, core coverage, advanced utilization, progression, and major-preparation evidence. School offerings are never inferred from country. When `advanced_courses_available` is zero, rule `ACAD-005` applies the documented neutral-context score and returns `no_advanced_penalty: true`. The endpoint is public, stateless, rate-limited, and returns `Cache-Control: no-store`.

## College media and selectivity filters

College list queries also accept `institution_type` and `selectivity_band`. Supported selectivity bands are `UNDER_10`, `10_TO_20`, `20_TO_40`, `OVER_40`, and `UNKNOWN`; they are factual buckets derived from the latest published acceptance-rate snapshot, not applicant probabilities. List results expose the latest test policy, aid policy, and optional primary media. College detail results expose all verified `media` records with license, attribution, alt text, dimensions, source URL, and verification date.
