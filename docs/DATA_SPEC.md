# DATA_SPEC.md

# Web Data & Persistence Specification

**Version:** 2.0.0  
**Database:** Supabase PostgreSQL  
**Auth identity:** Supabase Auth `user.id`  
**ORM:** SQLAlchemy 2.x  
**Migrations:** Alembic

---

## 1. Principles

- PostgreSQL is the only persistent production database.
- Vercel local filesystem is temporary.
- user-owned rows must be scoped to authenticated owner;
- college reference data is cycle-versioned;
- every verified critical college fact has source provenance;
- raw essays/LORs are opt-in persistence;
- evaluations preserve rubric/engine versions.

---

## 2. IDs

Domain primary keys:

```text
UUID
```

External auth identity:

```text
auth_subject UUID/TEXT UNIQUE
```

Do not expose sequential database identifiers.

---

## 3. Core Enums

```text
ApplicantType:
DOMESTIC | INTERNATIONAL | UNKNOWN

ConfidenceLevel:
HIGH | MEDIUM | LOW

TestPolicy:
REQUIRED | OPTIONAL | FLEXIBLE | BLIND | NOT_ACCEPTED | UNKNOWN

NeedPolicy:
NEED_BLIND | NEED_AWARE | NO_NEED_BASED_AID | UNKNOWN

RequirementStatus:
REQUIRED | OPTIONAL | RECOMMENDED | NOT_REQUIRED | UNKNOWN

CompletionStatus:
MISSING | PRESENT | SUBMITTED | NOT_APPLICABLE | NOT_EVALUATED

PlanningCategory:
HIGH_REACH | REACH | COMPETITIVE | LIKELY_ISH | INSUFFICIENT_DATA

DataFreshness:
CURRENT | REVIEW_SOON | STALE | UNKNOWN
```

---

## 4. users

```text
id UUID PK
auth_subject TEXT UNIQUE NOT NULL
email_snapshot TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
deleted_at TIMESTAMPTZ NULL
```

Email snapshot is optional and must not be treated as auth authority.

---

## 5. applicant_profiles

```text
id UUID PK
user_id UUID FK NOT NULL
profile_name TEXT NOT NULL
applicant_type TEXT NOT NULL
country_code CHAR(2) NULL
graduation_year INTEGER NULL
curriculum_type TEXT NULL
grading_scale_name TEXT NULL
grading_scale_min NUMERIC NULL
grading_scale_max NUMERIC NULL
intended_major TEXT NULL
school_name TEXT NULL
class_size INTEGER NULL
class_rank INTEGER NULL
max_family_contribution NUMERIC NULL
budget_currency CHAR(3) NULL
requires_need_based_aid BOOLEAN NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

Ownership index:

```text
(user_id, id)
```

---

## 6. academic_terms

```text
id UUID PK
profile_id UUID FK
term_order INTEGER
term_name TEXT
school_year TEXT
average_grade NUMERIC NULL
scale_min NUMERIC NULL
scale_max NUMERIC NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

Unique:

```text
(profile_id, term_order)
```

---

## 7. courses

```text
id UUID PK
profile_id UUID FK
term_id UUID FK NULL
course_name TEXT
subject_area TEXT NULL
course_level TEXT NULL
grade_value NUMERIC NULL
grade_text TEXT NULL
is_advanced BOOLEAN NULL
is_highest_available BOOLEAN NULL
is_major_related BOOLEAN NULL
```

---

## 8. school_context

```text
id UUID PK
profile_id UUID FK UNIQUE
advanced_courses_available INTEGER NULL
advanced_program_types JSONB NULL
highest_course_levels JSONB NULL
notes TEXT NULL
```

---

## 9. test_scores

```text
id UUID PK
profile_id UUID FK
test_type TEXT
composite_score NUMERIC NULL
section_scores JSONB NULL
test_date DATE NULL
is_official BOOLEAN NULL
created_at TIMESTAMPTZ
```

---

## 10. activities

```text
id UUID PK
profile_id UUID FK
activity_order INTEGER NULL
activity_name TEXT
position_title TEXT NULL
organization_name TEXT NULL
description TEXT NULL
category TEXT NULL
hours_per_week NUMERIC NULL
weeks_per_year NUMERIC NULL
start_date DATE NULL
end_date DATE NULL
duration_months INTEGER NULL
participant_count INTEGER NULL
people_impacted INTEGER NULL
leadership_level TEXT NULL
recognition_scope TEXT NULL
progression_level INTEGER NULL
is_founder BOOLEAN DEFAULT FALSE
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

## 11. honors

```text
id UUID PK
profile_id UUID FK
honor_name TEXT
scope TEXT NULL
placement TEXT NULL
participant_count INTEGER NULL
selection_rate NUMERIC NULL
organizer TEXT NULL
countries_represented INTEGER NULL
academic_area TEXT NULL
grade_received TEXT NULL
repeat_count INTEGER DEFAULT 1
```

---

## 12. essays

```text
id UUID PK
profile_id UUID FK NULL
user_id UUID FK NOT NULL
essay_type TEXT
title TEXT NULL
prompt_text TEXT NULL
word_limit INTEGER NULL
min_words INTEGER NULL
raw_text TEXT NULL
save_raw_text BOOLEAN DEFAULT FALSE
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

Anonymous analysis does not create an `essays` row.

If `save_raw_text = false`, raw text must be NULL after evaluation.

---

## 13. essay_metrics

```text
id UUID PK
essay_id UUID FK
word_count INTEGER
character_count INTEGER
sentence_count INTEGER
paragraph_count INTEGER
avg_sentence_length NUMERIC
median_sentence_length NUMERIC
sentence_length_stddev NUMERIC
avg_paragraph_length NUMERIC
flesch_reading_ease NUMERIC NULL
flesch_kincaid_grade NUMERIC NULL
lexical_diversity NUMERIC NULL
reflection_density NUMERIC NULL
specificity_density NUMERIC NULL
repetition_rate NUMERIC NULL
metrics_version TEXT
created_at TIMESTAMPTZ
```

---

## 14. recommendations

Same retention principle as essays.

```text
id UUID PK
profile_id UUID FK
user_id UUID FK
recommender_role TEXT NULL
relationship_duration_months INTEGER NULL
raw_text TEXT NULL
save_raw_text BOOLEAN DEFAULT FALSE
content_hash TEXT
created_at TIMESTAMPTZ
```

---

## 15. colleges

```text
id UUID PK
slug TEXT UNIQUE
name TEXT
normalized_name TEXT
ipeds_id TEXT NULL
country_code CHAR(2)
state_region TEXT NULL
institution_type TEXT NULL
official_website TEXT NULL
common_app_member BOOLEAN NULL
city TEXT NULL
application_platform_primary TEXT NULL
application_platforms JSONB NOT NULL DEFAULT '[]'
active BOOLEAN DEFAULT TRUE
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

## 16. college_admissions

Historical by cycle:

```text
id UUID PK
college_id UUID FK
academic_cycle TEXT
applicants_total INTEGER NULL
admits_total INTEGER NULL
enrolled_total INTEGER NULL
acceptance_rate NUMERIC NULL
international_applicants INTEGER NULL
international_admits INTEGER NULL
sat_25 NUMERIC NULL
sat_50 NUMERIC NULL
sat_75 NUMERIC NULL
act_25 NUMERIC NULL
act_50 NUMERIC NULL
act_75 NUMERIC NULL
test_policy TEXT
```

Unique:

```text
(college_id, academic_cycle)
```

---

## 17. college_requirements

```text
id UUID PK
college_id UUID FK
academic_cycle TEXT
requirement_type TEXT
status TEXT
details TEXT NULL
deadline TIMESTAMPTZ NULL
word_limit INTEGER NULL
quantity INTEGER NULL
```

---

## 18. college_financial_aid

```text
id UUID PK
college_id UUID FK
academic_cycle TEXT
need_policy TEXT
international_need_based_aid BOOLEAN NULL
meets_full_demonstrated_need BOOLEAN NULL
css_profile_required BOOLEAN NULL
estimated_cost_of_attendance NUMERIC NULL
tuition NUMERIC NULL
room_board NUMERIC NULL
books_personal NUMERIC NULL
currency CHAR(3) DEFAULT 'USD'
notes TEXT NULL
```

---

## 19. college_cds_factors

```text
id UUID PK
college_id UUID FK
academic_cycle TEXT
factor_name TEXT
importance TEXT
```

Unique:

```text
(college_id, academic_cycle, factor_name)
```

---

## 20. college_sources

```text
id UUID PK
college_id UUID FK
field_group TEXT
field_name TEXT
source_type TEXT
source_url TEXT
academic_cycle TEXT NULL
retrieved_at TIMESTAMPTZ
verified_at TIMESTAMPTZ NULL
freshness TEXT
confidence TEXT
value_hash TEXT NULL
notes TEXT NULL
```

Verified data cannot omit source URL.

---

## 21. college_media

Curated institutional logos and campus imagery with explicit provenance. Only approved, licensed sources
may be imported; arbitrary search-engine image URLs are prohibited.

```text
id UUID PK
college_id UUID FK NOT NULL
media_type TEXT NOT NULL
image_url TEXT NOT NULL
source_url TEXT NOT NULL
license TEXT NOT NULL
attribution TEXT NULL
alt_text TEXT NOT NULL
is_primary BOOLEAN DEFAULT FALSE
width INTEGER NULL
height INTEGER NULL
sha256 TEXT NULL
content_type TEXT NULL
verification_quality TEXT NULL
trademark_notice BOOLEAN NULL
verified_at TIMESTAMPTZ NOT NULL
```

Unique:

```text
(college_id, image_url)
(college_id, media_type) WHERE is_primary = TRUE
```

---

## 22. target_colleges

```text
id UUID PK
profile_id UUID FK
college_id UUID FK
priority INTEGER NULL
application_round TEXT NULL
application_status TEXT NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

Unique:

```text
(profile_id, college_id)
```

---

## 23. evaluations

```text
id UUID PK
user_id UUID FK NULL
profile_id UUID FK NULL
evaluation_type TEXT
subject_entity_id UUID NULL
college_id UUID FK NULL
engine_version TEXT
rubric_version TEXT
overall_score NUMERIC NULL
display_score INTEGER NULL
confidence TEXT
status TEXT
input_hash TEXT
evaluation_date DATE
evaluated_at TIMESTAMPTZ
created_at TIMESTAMPTZ
```

Anonymous evaluation results are returned directly and not persisted by default.

---

## 24. evaluation_components

```text
id UUID PK
evaluation_id UUID FK
component_name TEXT
score NUMERIC NULL
weight NUMERIC NULL
weighted_value NUMERIC NULL
status TEXT
```

---

## 25. triggered_rules

```text
id UUID PK
evaluation_id UUID FK
rule_id TEXT
rule_version TEXT
severity TEXT
category TEXT
message TEXT
score_delta NUMERIC NULL
confidence TEXT
evidence JSONB
created_at TIMESTAMPTZ
```

---

## 26. application_material_status

```text
id UUID PK
profile_id UUID FK
college_id UUID FK
requirement_type TEXT
completion_status TEXT
linked_entity_id UUID NULL
notes TEXT NULL
updated_at TIMESTAMPTZ
```

---

## 27. saved_reports

```text
id UUID PK
user_id UUID FK
profile_id UUID FK
report_type TEXT
report_version TEXT
report_json JSONB
created_at TIMESTAMPTZ
```

Do not duplicate raw essay/LOR text inside report JSON.

---

## 28. rate_limit_buckets

For lightweight DB-backed application limits:

```text
id BIGSERIAL PK
subject_hash TEXT
route_key TEXT
window_start TIMESTAMPTZ
request_count INTEGER
expires_at TIMESTAMPTZ
```

Anonymous IP identifiers must be salted/hashed before storage.

---

## 29. admin_import_runs

```text
id UUID PK
admin_user_id UUID FK
import_type TEXT
academic_cycle TEXT NULL
status TEXT
rows_read INTEGER
rows_valid INTEGER
rows_rejected INTEGER
diff_summary JSONB
created_at TIMESTAMPTZ
approved_at TIMESTAMPTZ NULL
```

---

## 30. Source Staging

Use staging tables or isolated schema:

```text
staging.colleges
staging.admissions
staging.requirements
staging.financial_aid
staging.cds_factors
staging.sources
```

Promotion requires validation and explicit admin approval.

---

## 31. User Data Deletion

Account deletion removes user-owned:

- profiles;
- academic terms/courses;
- tests;
- activities;
- honors;
- essays and saved text;
- recommendations;
- target colleges;
- evaluations;
- application status;
- saved reports.

Reference college data remains.

---

## 32. Security and Ownership

Every authenticated query must be scoped to verified owner.

Never accept:

```text
user_id from request body
```

as authorization.

Use verified auth subject → internal user → ownership filter.

---

## 33. Migration Policy

- Alembic migration for every production schema change.
- Never mutate production schema manually.
- Migrations must be reversible where practical.
- migration version checked during deployment/health check.
