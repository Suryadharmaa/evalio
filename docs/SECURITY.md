# SECURITY.md

# Web Security & Privacy Specification

**Version:** 2.0.0  
**Deployment:** Vercel + Supabase  
**Threat model:** Public internet application

---

## 1. Primary Assets

Protect:

- Supabase/Auth credentials;
- database credentials;
- user accounts;
- essays;
- recommendation letters;
- academic records;
- financial preferences;
- saved reports;
- verified college data.

---

## 2. Authentication

Use Supabase Auth.

Protected API:

```text
Authorization: Bearer <access_token>
```

Python backend must verify token before trusting identity.

Validate:

- signature;
- issuer;
- audience where configured;
- expiration;
- subject.

Never trust session/user information merely decoded on client.

---

## 3. Authorization

All private resources are owner-scoped.

Pattern:

```text
verified token sub
→ internal user
→ query WHERE user_id = verified user
```

Never authorize from:

- request body's user ID;
- email text;
- frontend role flag.

Admin rights come only from server-side configuration or trusted database role mapping.

---

## 4. Secrets

Server-only:

```text
DATABASE_URL
SUPABASE_SECRET_KEY
ADMIN_USER_IDS
IP_HASH_SALT
```

Public browser-safe:

```text
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
```

Never expose database passwords or secret/service keys to frontend bundles.

---

## 5. XSS

Treat all user content as untrusted.

Default:

- render essay/LOR as plain text;
- do not use unsafe raw HTML;
- escape filenames/titles;
- sanitize any future rich text.

Never pass user text into `dangerouslySetInnerHTML` without a reviewed sanitizer.

---

## 6. CSRF

Prefer Bearer-token API authorization rather than ambient cross-site credentials for Python API.

For cookie-based state-changing Next.js actions, use framework-supported same-site protections and CSRF-safe patterns.

All destructive actions require POST/DELETE, never GET.

---

## 7. CORS

Production API is same-origin under the Vercel domain.

Default:

```text
allow only configured application origins
```

Do not use wildcard CORS with credentials.

---

## 8. File Upload Security

Supported:

```text
txt
md
docx
pdf
csv
```

Product-level direct upload max:

```text
4 MB
```

Reject:

- encrypted PDFs;
- executables;
- archives;
- macro-enabled Office documents;
- unknown binaries;
- scanned/image-only PDF in V1.

Generate server-side temp filenames. Never use raw client filename as filesystem path.

---

## 9. Ephemeral Files

Vercel temporary processing only.

Always cleanup in `finally`.

Do not persist raw upload to database/storage unless a future explicit-save flow is designed.

---

## 10. Input Validation

Use:

- Zod frontend for UX;
- Pydantic backend as authority.

Validate:

- string lengths;
- numeric ranges;
- dates;
- enums;
- page counts;
- row counts;
- max list sizes;
- content size.

Frontend validation is never a security boundary.

---

## 11. SQL Security

Use SQLAlchemy parameterized queries.

No dynamic SQL interpolation from user strings.

Administrative import code must validate identifiers and enum mappings.

---

## 12. Rate Limiting

Public internet endpoints require rate controls.

Recommended initial application limits:

```text
essay analyze          20/hour/subject
activity analyze       40/hour/subject
college search        120/hour/subject
college evaluate       30/hour/auth-user
report                  10/hour/auth-user
```

Anonymous identity:

```text
hash(IP + rotating/server salt)
```

Do not persist raw IP longer than operationally needed.

---

## 13. Resource Limits

```text
essay text max          100,000 chars
direct file upload      4 MB
activities/profile      50
honors/profile          50
college compare         10
CSV rows             5,000
report JSON response < platform payload limit
```

---

## 14. Logs

Allowed:

- request ID;
- route;
- status;
- latency;
- internal user ID or anonymous hash;
- error code;
- engine/rubric version.

Forbidden:

- access/refresh tokens;
- password;
- raw essay/LOR;
- transcript body;
- raw file;
- database secret;
- Supabase secret key;
- detailed family-finance values.

---

## 15. Privacy Defaults

Anonymous:

```text
no content persistence
```

Authenticated:

```text
structured profile persistence allowed
raw essay/LOR persistence opt-in
```

Do not request unnecessary sensitive identity documents.

---

## 16. Protected Characteristics

Never numerically score:

- race;
- ethnicity;
- religion;
- sex;
- sexual orientation;
- disability;
- political affiliation;
- medical status.

---

## 17. Account Export

`Export my data` must include only verified user's:

- profile;
- academics;
- activities;
- honors;
- tests;
- target colleges;
- saved evaluations/reports;
- saved essay/LOR text if opted in.

Do not include internal secrets or other users.

---

## 18. Account Deletion

Deletion requires re-authenticated/current session and explicit confirmation.

Delete user-owned records and saved private text.

Reference college data remains.

Return a completion response only after DB transaction succeeds.

---

## 19. Admin Security

Admin APIs:

- authentication required;
- server-side role check;
- audit log;
- destructive changes require explicit confirmation;
- imports use staging;
- no direct public route to production data overwrite.

---

## 20. Source Integrity

Critical college facts require provenance.

Do not mark a fact VERIFIED without:

```text
source URL
cycle
verification time
confidence
```

---

## 21. Dependency Security

Use lockfiles:

```text
pnpm-lock.yaml
uv.lock or pinned Python lock strategy
```

Run periodic vulnerability checks.

Avoid unnecessary packages.

---

## 22. Deployment Security

Separate:

```text
Preview
Production
```

Preview deployments should use non-production data where possible.

Never expose production secrets in pull-request logs.

---

## 23. Headers

Recommended:

- Content-Security-Policy;
- X-Content-Type-Options;
- Referrer-Policy;
- Permissions-Policy;
- strict transport via Vercel HTTPS;
- secure SameSite cookie settings for auth libraries where applicable.

CSP must be tested with Supabase Auth resources actually used.

---

## 24. Error Handling

User sees:

```text
Unable to analyze this file because it contains no extractable text.
```

Never expose:

- stack trace;
- database query;
- local temp path;
- environment variable;
- secret;
- auth token.

---

## 25. Security Release Blockers

Release is blocked if:

- user A can access user B data;
- token/secret appears in frontend bundle;
- raw essay appears in logs;
- private endpoint accepts unverified identity;
- upload traversal is possible;
- direct production import bypasses staging;
- account deletion leaves saved raw private text;
- AI/LLM dependency has been introduced contrary to product spec.
