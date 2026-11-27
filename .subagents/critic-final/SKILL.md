---
name: critic-final
description: "Grade the round: preflight all six sub-agent folders, audit the parent agent's claims, and score 1-10 against the rubric, blocking the round below 7."
---

# Critic: Final

## When to use

Use last in every round, after every other sub-agent has run and left its report. Not in the middle of a round: a grade of incomplete work is noise that hides the real gaps.

Run this last, every round. Nothing ships on a score below 7/10.

## Why this exists

The owner's rule: "Der criticer bewertet, wenn du 10/10 hast bist der Beste, wenn
du unter 7/10 bist musst du die Findings beheben." A self-assessment is not a
review; a grader with a rubric, a preflight and a pass mark is.

## Procedure

1. **Preflight.** `python3 codegraph.py --json reports/latest.json` walks the six
   folders and reports, per folder: the four required files, the skill
   frontmatter (ASCII, `name` == directory, quoted description), a report, and a
   proposals file. Missing items are deductions, not notes.
2. **Score.** Apply the rubric in `ORIGINAL.md` (2+1+2+2+2+1 points).
3. **Sample the evidence.** Take three claims from the session log and three from
   the sub-agent proposals; demand the command, the `file:line` or the URL.
4. **Run the protocol gates** yourself rather than trusting the claim that they
   are green: `bash tools/session_start_check.sh` and
   `bash tools/docs_claim_check.sh`.
5. **Write `REVIEW.md`.** Score, per-criterion verdict, findings ordered by
   severity, and — below 7 — the exact fix list the parent must apply first.

## Scoring rules

- Met means "shown", not "likely".
- A stub, a placeholder or a fake checkbox in any folder is an automatic 1-point
  deduction under criterion 6, and it may not be outweighed by anything else.
- Re-run after the fixes; a fixed finding that regresses is scored again.
- Never adjust the rubric to fit the result.

## Anti-patterns

- Awarding 10/10 without opening `reports/latest.json` of every folder.
- Reviewing only the parent and skipping the other five sub-agents (the owner
  explicitly asked for the cross-check).
- Writing "minor issues" without naming them.
