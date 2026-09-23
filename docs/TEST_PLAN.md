# TEST_PLAN.md

# Web Test & Quality Plan

**Version:** 2.0.0

---

## 1. Quality Goal

Guarantee:

```text
same input + same data snapshot + same rule version = same evaluation
```

and ensure the web application does not weaken privacy, authorization, or deterministic scoring.

---

## 2. Test Layers

```text
tests/
├── python/
│   ├── unit/
│   ├── rules/
│   ├── integration/
│   ├── database/
│   ├── parsers/
│   ├── regression/
│   └── golden/
├── frontend/
│   ├── components/
│   ├── forms/
│   └── api-client/
└── e2e/
    ├── public/
    ├── authenticated/
    ├── mobile/
    └── accessibility/
```

---

## 3. Python Tooling

```text
pytest
pytest-asyncio
coverage
```

Required checks:

```text
ruff
mypy
pytest
```

---

## 4. Frontend Tooling

Recommended:

```text
Vitest
React Testing Library
Playwright
```

Run type checking:

```text
tsc --noEmit
```

---

## 5. Rule Tests

Every rule needs:

- trigger case;
- non-trigger case;
- exact threshold boundary;
- evidence assertion;
- score impact assertion;
- deterministic ordering assertion where relevant.

---

## 6. Golden Tests

Maintain synthetic benchmark fixtures for:

- essays;
- academic profiles;
- activities;
- honors;
- LORs;
- college evaluations.

Golden output includes:

```text
engine_version
rubric_version
overall_score
components
triggered rule IDs
confidence
```

---

## 7. API Contract Tests

For every endpoint:

- success schema;
- validation failure;
- authentication requirement;
- ownership check;
- not found;
- rate limit;
- internal error sanitization.

Verify error envelope matches `API_SPEC.md`.

---

## 8. Authentication Tests

Required:

- valid Supabase token;
- expired token;
- malformed token;
- wrong issuer;
- missing token on protected endpoint;
- anonymous access to public endpoint;
- user A cannot access user B profile;
- admin endpoint rejects normal user.

---

## 9. Upload Tests

- TXT success;
- DOCX success;
- text PDF success;
- scanned PDF → NO_EXTRACTABLE_TEXT;
- encrypted PDF rejected;
- malformed document;
- 4 MB boundary;
- >4 MB rejected before expensive processing;
- traversal filename ignored;
- temporary cleanup after success/error.

---

## 10. Database Tests

Use test PostgreSQL where integration requires production-like semantics.

Test:

- migrations;
- FK constraints;
- unique constraints;
- JSONB evidence;
- owner scoping;
- cascade deletion;
- source-cycle history;
- raw essay storage default off.

SQLite must not be used as a substitute for PostgreSQL-specific integration tests.

---

## 11. Frontend Component Tests

Required for:

- score card;
- rule issue list;
- profile forms;
- essay input;
- college comparison;
- loading/error/empty states;
- confidence badge;
- methodology details.

Score labels must not rely on color alone.

---

## 12. End-to-End Flows

### Anonymous essay

```text
visit /essay
paste essay
analyze
see score/components/issues
refresh
confirm analysis not saved
```

### Auth profile

```text
sign in
create profile
add academics
add activity
save
reload
confirm persistence
```

### College evaluation

```text
open college
evaluate with saved profile
view why-result
```

### Delete account data

```text
request deletion
confirm
verify protected resources unavailable
```

---

## 13. Mobile E2E

Test at least:

```text
360x800
390x844
768x1024
```

All core workflows must work without horizontal scrolling.

---

## 14. Accessibility Tests

Automated + manual:

- keyboard navigation;
- focus order;
- labels;
- error association;
- heading hierarchy;
- modal focus trap;
- reduced motion;
- contrast;
- screen-reader-friendly score text.

---

## 15. Security Tests

- XSS payload in essay/title;
- SQL injection strings;
- forged user ID;
- forged admin flag;
- CSRF-sensitive state changes where applicable;
- dangerous URL schemes;
- oversized JSON;
- upload type mismatch;
- auth token in log redaction;
- raw essay in log redaction.

---

## 16. Determinism Test

Run same evaluation repeatedly.

Assert identical:

- internal scores;
- display score;
- triggered rules;
- rule order;
- evidence;
- confidence.

Exclude request IDs/timestamps from comparison.

---

## 17. Performance Tests

Targets:

```text
650-word essay typical API <2.5s
college evaluation <2s
activity evaluation <1s
public page LCP target <2.5s
```

Regression thresholds should be tracked, not blindly fail on noisy CI.

---

## 18. Data Import Tests

- invalid admit rate;
- SAT percentile inversion;
- duplicate source;
- unknown enum;
- stale cycle;
- source missing;
- diff generation;
- no production promotion without approval.

---

## 19. Coverage Targets

Recommended:

```text
Python engine/rules >= 90%
critical scoring rules = 100% boundary coverage
repositories >= 80%
API routers/services >= 85%
frontend business components >= 80%
```

---

## 20. Release Gate

```text
[ ] Python tests pass
[ ] frontend tests pass
[ ] Playwright critical flows pass
[ ] ruff clean
[ ] mypy clean for engine/API
[ ] TypeScript typecheck clean
[ ] no unexpected golden diff
[ ] migrations tested
[ ] auth ownership tests pass
[ ] upload cleanup tests pass
[ ] no prohibited AI dependency
[ ] production build succeeds
```
