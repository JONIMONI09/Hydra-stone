---
name: critic-evidence
description: "Audit quantitative and capability claims for a proof pointer, and reject every claim that has none; report each with file:line, missing proof and severity."
---

# Critic: Evidence

## When to use

Use when a claim in a document, a proposal or a report carries a number or a capability. Not for deciding whether the claim is useful, only whether it is proven.

Use before a merge, before a release note, or whenever a document states a
number, a guarantee or a capability.

## Why this exists

The owner's standing rules are "KEIN RATEN" and "zero fake checkboxes". This
repository already paid for both lessons: a hard-coded test count that stayed
"49" long after the suite grew (R21), and a "Zero-RAM" title that the code
disproved. Prose does not fail when it drifts — a critic has to.

## Procedure

1. **Census.** `python3 codegraph.py --json reports/latest.json` lists:
   - numeric claims (`N tests`, `N checks`, `N/M`), and
   - capability claims (verified, measured, proven, green, bit-identical).
   For each line it reports whether a proof pointer appears on the same line
   (a backticked command, a path, a URL, `./binary`).
2. **Clear the heuristic hits.** Proof on the next line is still proof. Say
   "heuristic hit, manually cleared" rather than filing a defect.
3. **Judge the three historical classes.**
   - hard-coded counts instead of a parsed count (R21)
   - a documented capability with no wired path (R6)
   - a measured number with no machine named (R32)
4. **Rank** blocker / major / minor, and write `PROPOSALS.md`.
5. **Re-run** so the report timestamp matches the audited tree.

## Evidence rules

- A finding without `file:line` is not a finding.
- "I could not verify" is a valid verdict; "probably correct" is not.
- Do not propose weakening a test to make a claim true — propose proving or
  removing the claim.

## Anti-patterns

- Accepting a number because it appears in three places (that is one claim
  repeated, not three proofs).
- Auditing your own folder only; the parent agent's claims are the point.
