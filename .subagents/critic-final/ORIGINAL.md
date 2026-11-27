# ORIGINAL.md — `critic-final`

> Created **before this sub-agent's first run** (owner directive 2026-10-29).
> Immutable assignment record: never edited after creation; a changed remit
> gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `critic-final` |
| Kind | critic (3 of 3 critics, 6 of 6) — the graded reviewer |
| Created | 2026-10-29 |
| Created by | parent agent (round 12) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` (merge of PR #70) |
| Web access | allowed, to confirm a claim made by the parent agent |

## Original owner assignment (verbatim, German)

> "Am Ende IMMER einen criticer starten der deine Arbeit kritisieren muss etc und Fehler finden muss etc !!! Criticer soll auch in den andren Sub Agents schauen"
> "Der criticer bewertet wenn du 10/10 hast bist der Beste wenn du unter 7/10 bist musst du fibdings beheben"

## Normalised assignment (English)

Run last, every round. Judge the parent agent's work **and** the other five
sub-agent folders against the rubric below, find the errors, and score 1-10. A
score below 7/10 blocks the round: the findings must be fixed and the review
re-run until the score is at least 7. A 10/10 means every criterion is met with
evidence; it is not a courtesy.

## Rubric (10 points)

| # | Criterion | Points |
|---|---|---|
| 1 | Structure: six folders, each with `ORIGINAL.md`, `AGENTS.md`, `SKILL.md`, `codegraph.py`, `reports/` | 2 |
| 2 | Skills follow the Agent Skills spec: frontmatter ASCII, `name` == directory, quoted one-sentence description (R29/R30) | 1 |
| 3 | Every `codegraph.py` runs and reports the real tree (file count, mtimes, all `.md`, open work) | 2 |
| 4 | Evidence: every claim made by a sub or the parent has a command output, a `file:line` or a URL | 2 |
| 5 | Protocol: R33 marker, session/errors/user records updated, English artefacts, gates green | 2 |
| 6 | No stubs, no fake checkboxes, no invented data anywhere in `.subagents/` | 1 |

Scores below 7 must be accompanied by the exact list of fixes; the parent
applies them and re-runs this critic.

## Deliverables

| File | Meaning |
|---|---|
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R30) |
| `codegraph.py` | read-only repository graph + the preflight of all six folders |
| `reports/latest.txt`, `reports/latest.json` | generated evidence of the last run |
| `REVIEW.md` | the graded review (this sub's only prose artefact) |

## Acceptance criteria

1. Every deduction names the rule, the file and the evidence.
2. The preflight numbers in `REVIEW.md` match `reports/latest.json`.
3. A reviewed folder is judged on its own claims, not on its author's intent.
4. Nothing outside this folder is modified.
