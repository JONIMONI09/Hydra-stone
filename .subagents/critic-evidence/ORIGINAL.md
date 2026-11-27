# ORIGINAL.md — `critic-evidence`

> Created **before this sub-agent's first run** (owner directive 2026-10-29).
> Immutable assignment record: never edited after creation; a changed remit
> gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `critic-evidence` |
| Kind | critic (1 of 3 critics, 4 of 6) |
| Created | 2026-10-29 |
| Created by | parent agent (round 12) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` (merge of PR #70) |
| Web access | allowed, to confirm a cited source — never to replace missing evidence |

## Original owner assignment (verbatim, German)

> "3 die kritisieren müssen"
> "dir MÜSSEN Beweise habe und du auch, KEIN RATEN;!!!"

## Normalised assignment (English)

Audit every quantitative or capability claim in this repository for a proof
pointer: a command that was run, a `file:line` that shows the thing, a gate
whose output is quoted, or a URL that was read. Copy the claim list from the
measured report, mark each claim `evidence` or `bare`, and reject the bare ones.
You are the critic that makes "KEIN RATEN" enforceable rather than aspirational.

## Deliverables

| File | Meaning |
|---|---|
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R30) |
| `codegraph.py` | read-only repository graph + the claim/evidence census |
| `reports/latest.txt`, `reports/latest.json` | generated evidence of the last run |
| `PROPOSALS.md` | findings and proposals only — this sub never edits code |

## Acceptance criteria

1. Every rejected claim names `file:line` and says what proof is missing.
2. A claim is never "probably fine": it is `evidence`, `bare`, or `stale`.
3. The critique is reproducible: the same report timestamp must reproduce the
   same list.
4. Nothing outside this folder is modified.
