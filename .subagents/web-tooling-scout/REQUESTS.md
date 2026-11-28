# Requests — `web-tooling-scout`

| # | Question | Status |
|---|---|---|
| R-1 | Should `tools/kotlin_stub_check/kotlin_stub_check.sh` run in CI instead of staying manual? | answered |
| R-2 | Which tools lack an install path in `.agents/Environment.md`? | open |
| R-3 | Should CI pin the `cppcheck` version it installs? | open |

## R-1 — the stub gate in CI (answered 2026-10-29)

**Answer.** No. CI compiles the real Kotlin through Gradle (`ci.yml:739`,
`lint.yml:548`); the stub gate exists for sandboxes without the Android SDK and
would cost CI minutes to re-check what Gradle already proves. Documented as
manual-only in `AGENTS.md` §3.

## R-2 — install paths

**Why it matters.** A gate whose tool cannot be installed from the docs is a
gate that only one machine can run.

**Recommendation.** Add a one-line install per missing tool to
`.agents/Environment.md`; the audit lists the candidates every run.

## R-3 — pinned tool versions

**Recommendation.** Pin `cppcheck` (and any linter whose output feeds a gate):
an unpinned linter turns a green build red on someone else's release day.
