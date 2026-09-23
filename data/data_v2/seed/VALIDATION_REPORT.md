# Evalio College Research — Batch 1 Validation Report

**Research date:** 2026-09-14

## Result

- Institutions processed: **200**
- Unique slugs: **200**
- IPEDS IDs available: **200**
- Critical campus/institution misbindings corrected: **4**
- Validation errors after correction: **0**
- Provenance/source records: **632**

## Coverage

| Field | Filled |
|---|---:|
| Acceptance rate | 200/200 |
| Applicants total | 4/200 |
| SAT 25th | 172/200 |
| SAT median | 2/200 |
| SAT 75th | 172/200 |
| ACT 25th | 174/200 |
| ACT median | 3/200 |
| ACT 75th | 174/200 |
| Application fee | 2/200 |
| Tuition baseline | 200/200 |
| Estimated COA | 150/200 |
| Known international-aid policy | 8/200 |
| Official website verified in current seed | 12/200 |
| Verified primary campus images | 3/200 |

## 2026–27 testing policy

{
  "OPTIONAL": 159,
  "REQUIRED": 25,
  "BLIND": 16
}

## International aid policy

{
  "NEED_BLIND": 8,
  "UNKNOWN": 192
}

## Critical identity corrections

Batch 1 corrected four dangerous fuzzy/campus matches:

1. Purdue University Global → **Purdue University-Main Campus (IPEDS 243780)**
2. West Texas A&M University → **Texas A&M University / College Station (IPEDS 228723)**
3. North Carolina A&T State University → **North Carolina State University at Raleigh (IPEDS 199193)**
4. Arizona State University-West → **Arizona State University Campus Immersion (IPEDS 104151)**

These corrections prevent Evalio from showing another institution's admissions or cost data under the intended college.

## Validation rules run

- exactly 200 colleges
- unique slug
- unique IPEDS ID
- acceptance rate 0–100
- SAT 400–1600
- ACT 1–36
- percentile ordering when all three percentiles exist
- non-negative tuition/COA
- COA >= tuition where both values exist

## Important limitation

This is **Batch 1, not the final all-fields production truth set**.

Core identity/admissions/testing/cost baseline is now much safer and normalized for all 200 schools,
but `research_gaps.csv` intentionally flags fields that still require direct official verification,
especially international need-based aid, full-need commitments, official websites, current application fees,
English-proficiency requirements, application deadlines, requirements, and campus media.

Do not convert UNKNOWN to NO.
Do not fill blanks with estimates.
