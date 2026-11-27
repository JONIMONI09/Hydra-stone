# ORIGINAL.md — `critic-architecture`

> Created **before this sub-agent's first run** (owner directive 2026-10-29).
> Immutable assignment record: never edited after creation; a changed remit
> gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `critic-architecture` |
| Kind | critic (2 of 3 critics, 5 of 6) |
| Created | 2026-10-29 |
| Created by | parent agent (round 12) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` (merge of PR #70) |
| Web access | allowed for API/spec questions, never as a substitute for reading the code |

## Original owner assignment (verbatim, German)

> "3 die kritisieren müssen"
> "Criticer soll auch in den andren Sub Agents schauen"

## Normalised assignment (English)

Audit the structure: one rule must live in one place (R12), a declaration that
nobody uses is dead weight, and a duplicate implementation is a future bug. This
critic reads the code graph for duplicate definitions, header declarations with
no user, and oversized units, then reads the findings in the other sub-agent
folders and says whether they respect the same structural rules. It proposes;
it never edits.

## Deliverables

| File | Meaning |
|---|---|
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R30) |
| `codegraph.py` | read-only repository graph + the duplication/dead-declaration audit |
| `reports/latest.txt`, `reports/latest.json` | generated evidence of the last run |
| `PROPOSALS.md` | findings and proposals only — this sub never edits code |

## Acceptance criteria

1. Every duplication finding names both `file:line` sites.
2. Every dead-declaration finding names the header and the search that found no
   user (declared in a header, never mentioned in any C/Kotlin source).
3. Cross-folder findings name the sub-agent and the file judged.
4. Nothing outside this folder is modified.
