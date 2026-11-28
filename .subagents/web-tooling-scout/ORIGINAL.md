# ORIGINAL.md — `web-tooling-scout`

> Created **before this sub-agent's first run** (owner directive 2026-10-29).
> Immutable assignment record: never edited after creation; a changed remit
> gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `web-tooling-scout` |
| Kind | web research (3 of 3 research, 3 of 6) |
| Created | 2026-10-29 |
| Created by | parent agent (round 12) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` (merge of PR #70) |
| Web access | required — package indexes and tool documentation |

## Original owner assignment (verbatim, German)

> "3 die im Websuchen können"
> "installiere skills etc"

## Normalised assignment (English)

Keep the verification toolchain honest and installable: for every gate script
in `tools/`, establish whether CI actually runs it; for every command the docs
tell a reader to run, establish whether the file exists; for every tool a gate
needs, record a tested install path (`.agents/Environment.md` discipline). A
gate nobody calls and a command that points at a deleted file are both silent
failures, which is what this sub-agent exists to surface.

## Deliverables

| File | Meaning |
|---|---|
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R30) |
| `codegraph.py` | read-only repository graph + the gate-wiring and command audit |
| `reports/latest.txt`, `reports/latest.json` | generated evidence of the last run |
| `PROPOSALS.md` | findings and proposals only — this sub never edits code |

## Acceptance criteria

1. Every "unwired gate" finding names the script and the workflow search that
   found no reference — or the Makefile target that does call it.
2. Every "documented command is missing" finding names `file:line` and the path
   that does not exist.
3. Install paths are recorded with the exact command and the exact error, never
   "should work" (owner rule: record the tested path in Environment.md).
4. Nothing outside this folder is modified.
