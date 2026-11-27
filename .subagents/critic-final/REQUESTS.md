# Requests — `critic-final`

| # | Question | Status |
|---|---|---|
| R-1 | Should the score be labelled "procedural" until a second model can review? | answered |
| R-2 | Is 7/10 the block threshold, or should a failed protocol gate (R33/R34) be an automatic block regardless of score? | open |
| R-3 | May the critic deduct for a limitation the parent cannot fix in this environment? | open |

## R-1 — labelling (answered 2026-10-29)

**Answer.** Yes. `REVIEW.md` names the limitation next to the score. A 9/10 that
hides "no independent reviewer" would be the courtesy point this rubric forbids.

## R-2 — automatic block on a failed gate

**Why it matters.** A round can score 8/10 on evidence and still ship a red
R33/R34 gate. Today the rubric treats protocol as 2 of 10 points.

**Recommendation.** Yes: add "a red R33 or R34 gate blocks the round regardless
of score". Safety first is already the rule order in `.agents/rules.md` §9.

## R-3 — deductions for environmental limits

**Recommendation.** No deduction for a limit that is stated and unavoidable; full
deduction for a limit that is stated as if it were not one.
