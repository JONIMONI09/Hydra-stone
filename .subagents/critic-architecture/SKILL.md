---
name: critic-architecture
description: "Judge structure in the code graph and in the other sub-agents' proposals: duplicate implementations, declarations nobody uses, and rules that live in two places instead of one."
---

# Critic: Architecture

## When to use

Use when a round added code or docs and someone must judge structure: duplicate implementations, declarations nobody uses, one rule living in two places.
Not for grading the round - that is `critic-final`.

Use before a merge that touches more than one module, after adding a second
implementation of anything, and when reviewing the `.subagents` team's output.

## Why this exists

R12 is the rule this repository breaks most expensively: "if a rule lives in two
places, one is a future bug." The history here is concrete — a batching policy
duplicated between C and JS, a sampler chain re-implemented per surface, a NEON
kernel that was silently deleted while its aggregation lived on. A duplicate is
not a style issue; it is a divergence waiting for the next edit.

## Procedure

1. **Duplicates.** `python3 codegraph.py --json reports/latest.json` lists
   function-like names defined in more than one source file. Both sites, or it
   is not a finding. Decide which side is canonical.
2. **Dead declarations.** The script lists `hydra_*` / `hydra2_*` names declared
   in `include/` and mentioned in no C or Kotlin file. Before filing, check the
   JNI bridge: a function called only through `System.loadLibrary` is not dead.
3. **Size.** The largest units are listed for the reader; growth alone is not a
   defect, so pair it with a concrete consequence (a function that no longer fits
   in a review, a file with two responsibilities).
4. **Peer review of the team.** Read each `.subagents/*/PROPOSALS.md`. A proposal
   that would create a second source of truth is rejected with the reason.
5. **Report** with both sites cited, then re-run.

## Evidence rules

- Two `file:line`s for duplication; a named search for dead code.
- "This looks duplicated" is not a finding; the same algorithm written twice is.
- Do not propose a refactor without naming the test that keeps the behaviour.

## Anti-patterns

- Filing a finding about a deliberate, documented split (e.g. the scalar and the
  SIMD kernel are compared by a parity test on purpose, R9).
- Treating a stub-check fixture as production duplication.
- Renaming or moving anything: this critic proposes only.
