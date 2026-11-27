# Error Log — `critic-evidence`

Append-only, newest last.

## 2026-10-29 — 532 "bare number" hits came from historical logs

**What happened.** The first census scanned every Markdown file, including
`CHANGELOG.md` and `docs/SESSION-ARCHIVE.md`, where numbers describe past
measurements and are correct in context. Reporting them as unproven claims made
the critic unusable.

**Evidence.** `532 bare-number candidates`, most with `CHANGELOG.md` as the path.

**What changed.** The census reads only documents a reader acts on today
(root `README.md`, `AGENTS.md`, `.agents/*`, `docs/*` minus the archive).
Live result: 12 candidates instead of 532.

## 2026-10-29 — the critic counted its own proposals as claims

**What happened.** `.subagents/*/PROPOSALS.md` names numbers in order to report
them, so the critic reported itself: 27 candidates, 15 of them self-referential.

**What changed.** `.subagents/` is excluded from the live corpus; the count
dropped to 12 and every remaining row is a real document.

## 2026-10-29 — the parent's own log quoted a secrecy phrase

**What happened.** `AGENTS.md` in the root carried four hard-coded test counts
(R21 says numbers need provenance). They were replaced with "count parsed from
output", and the check now reports 0 hits there.
