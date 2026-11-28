# Error Log — `web-tooling-scout`

Append-only, newest last.

## 2026-10-29 — the path pattern matched its own folder

**What happened.** Searching for `tools/` to find gate scripts also matched
`.subagents/tools/`, so the audit reported the sub-agents' own helpers as
repository gates.

**Evidence.** First table listed `.subagents/tools/check_subagents.py` under
"tooling the CI runs".

**What changed.** Paths are anchored at the repository root, and `.subagents/`
is excluded from the tool census.

## 2026-10-29 — historical logs were counted as live documentation

**What happened.** `CHANGELOG.md` and `docs/SESSION-ARCHIVE.md` describe past
gates; counting them as current documentation produced 532 "documented" claims
that no reader would follow today.

**What changed.** The census reads only documents a reader acts on (root
README, `AGENTS.md`, `.agents/*`, `docs/*` minus the archive).

## 2026-10-29 — `kotlinc` is not installed in this environment

**What happened.** The Kotlin stub gate could not be executed, so its wiring
could only be described, not measured. Reported as "blocked, not measured"
rather than assumed green.

**What changed.** Nothing in the tool; the limitation is now written down in
`AGENTS.md` §3 as "manual-only, on purpose" (round 13).
