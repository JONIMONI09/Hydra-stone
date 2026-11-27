# ORIGINAL.md — `web-source-verifier`

> Created **before this sub-agent's first run** (owner directive 2026-10-29:
> "before each one starts, an Original.MD must be created, because each has its
> own folder"). Immutable assignment record: never edited after creation; a
> changed remit gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `web-source-verifier` |
| Kind | web research (1 of 3 research, 1 of 6) |
| Created | 2026-10-29 |
| Created by | parent agent (round 12) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` (merge of PR #70) |
| Web access | required — primary sources only |

## Original owner assignment (verbatim, German)

> "3 die im Websuchen können"
> "KEIN RATEN;!!! [... ] dir MÜSSEN Beweise habe und du auch"

## Normalised assignment (English)

Verify every externally sourced statement this repository makes — version
pins, API behaviour, format constants, tool flags, security identifiers —
against the **primary** source (upstream repository, vendor documentation,
standards body) and cite the URL that was actually read. Produce a
verification queue for anything stated without a primary source, and a
correction proposal wherever the repository and the source disagree. Never
assert what was not read (R26).

## Deliverables

| File | Meaning |
|---|---|
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R30) |
| `codegraph.py` | read-only repository graph + the source census for this remit |
| `reports/latest.txt`, `reports/latest.json` | generated evidence of the last run |
| `PROPOSALS.md` | findings and proposals only — this sub never edits code |

## Acceptance criteria

1. Every finding names `file:line`; every external fact names the URL read.
2. A claim that cannot be verified is reported as unverified, never softened.
3. Nothing outside this folder is modified by this sub-agent.
4. Each proposal states what to change, where, and the risk of not changing it.
