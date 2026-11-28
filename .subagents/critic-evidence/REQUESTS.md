# Requests — `critic-evidence`

| # | Question | Status |
|---|---|---|
| R-1 | Is "count parsed from the command output" acceptable provenance, or must the number appear verbatim in the report? | open |
| R-2 | Should the 12 remaining bare-number claims be triaged in this round or in batches of five? | answered |
| R-3 | Do design documents (`docs/*-RESEARCH.md`) count as claims, or as plans? | open |

## R-1 — what counts as proof

**Why it matters.** `AGENTS.md` now says "count parsed from output" instead of
`109 checks`. That is honest but less checkable than a printed number.

**Recommendation.** Both: the report prints the number it measured, and the doc
states which command produces it. A number in prose with no command is a claim.

## R-2 — triage batches (answered 2026-10-29)

**Answer.** Batches of five, same round as the change that touches them. A
66-row backlog in one pass produces rubber-stamping, which is the failure the
critic exists to prevent.

## R-3 — plans versus claims

**Recommendation.** A plan may state a target ("target: under 50 ms"). It may not
state a result. The critic should flag past-tense measurements, not future
targets.
