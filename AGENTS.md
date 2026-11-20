<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->


<!-- BEGIN:evalio-utbk-cloud-rules -->
## Evalio UTBK/SNBT module (scoped instructions)
For tasks touching `/utbk`, `components/utbk`, PTN program data or the UTBK API, read `docs/utbk/README.md` and the relevant **one** task specification before editing.
- Preserve all existing international admissions features and CI.
- Use year-versioned UTBK rules; 2026 format is reference only until 2027 is verified.
- Keep answer keys, entitlements, and private attempts server-controlled; avoid unofficial admission probabilities.
- Reuse existing dependencies and visual identity. Prefer small, tested PRs.
- Start with EVAL-001 read-only audit. No unapproved production deployment, destructive migration, payment action, or merge.
- Choose scoped project skills from `.agents/skills/` only when relevant.
<!-- END:evalio-utbk-cloud-rules -->
